package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"time"

	"github.com/streadway/amqp"
)

type DeviceInfo struct {
	OS       string `json:"os"`
	Arch     string `json:"arch"`
	Hostname string `json:"hostname"`
}

type ServerResponse struct {
	ID string `json:"id"`
}

// Function to get device info without calling external commands
func getDeviceInfo() DeviceInfo {
	hostname, err := os.Hostname()
	if err != nil {
		log.Fatalf("Could not get hostname: %v", err)
	}
	return DeviceInfo{
		OS:       runtime.GOOS,
		Arch:     runtime.GOARCH,
		Hostname: hostname,
	}
}

func sendDeviceInfo(serverURL string, info DeviceInfo) (string, error) {
	data, err := json.Marshal(info)
	if err != nil {
		return "", err
	}

	resp, err := http.Post(serverURL, "application/json", bytes.NewBuffer(data))
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var response ServerResponse
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return "", err
	}

	return response.ID, nil
}

func sendToRabbitMQ(id, rabbitMQQueue, rabbitMQURL, filename string) error {
	fileData, err := os.ReadFile(filename) // Use os.ReadFile for reading file content in Go 1.16+
	if err != nil {
		return fmt.Errorf("failed to read file: %w", err)
	}

	conn, err := amqp.Dial(rabbitMQURL)
	if err != nil {
		return fmt.Errorf("failed to connect to RabbitMQ: %w", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		return fmt.Errorf("failed to open a channel: %w", err)
	}
	defer ch.Close()

	if err := ch.Confirm(false); err != nil {
		return fmt.Errorf("failed to enable publisher confirmations: %w", err)
	}

	_, err = ch.QueueDeclare(
		rabbitMQQueue,
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		return fmt.Errorf("failed to declare queue: %w", err)
	}

	confirmChan := ch.NotifyPublish(make(chan amqp.Confirmation, 1))


	message := amqp.Publishing{
		DeliveryMode: amqp.Persistent,
		ContentType:  "application/octet-stream",
		Body:         fileData,
		Headers: map[string]interface{}{
			"device_id": id,
		},
	}

	err = ch.Publish(
		"",
		rabbitMQQueue,
		false,
		false,
		message,
	)
	if err != nil {
		return fmt.Errorf("failed to publish message to RabbitMQ: %w", err)
	}

	select {
		case confirm := <-confirmChan:
			if confirm.Ack {
				log.Println(" [x] Message acknowledged by RabbitMQ")
				if err := os.Remove(filename); err != nil {
					log.Println("Failed to delete old file:", err)
				} else {
					log.Println("Deleted old file:", filename)
				}
				return nil
			} else {
				return sendToRabbitMQ(id, rabbitMQQueue, rabbitMQURL, filename)
			}
		case <-time.After(5 * time.Second):
			return fmt.Errorf("timeout waiting for RabbitMQ confirmation")
	}

}

func startPacketCapture(filename string) (*exec.Cmd, error) {
	if runtime.GOOS == "windows" {
		cmd := exec.Command("dumpcap", "-w", filename)
		err :=cmd.Start()
		return cmd, err

	} else {
		cmd := exec.Command("tcpdump", "-w", filename)
		err :=cmd.Start()
		return cmd, err
	}
}


func fileExists(filename string) bool {
    _, err := os.Stat(filename)
    if err == nil {
        return true 
    }
    if os.IsNotExist(err) {
        return false 
    }
    return false 
}

func getValue(filename string,key string) (string, error) {
    file, err := os.Open(filename)
    if err != nil {
        return "", err
    }
    defer file.Close()

    scanner := bufio.NewScanner(file)
    for scanner.Scan() {
        line := scanner.Text()
        if strings.HasPrefix(line, key) {
            
            return strings.TrimPrefix(line, key+"="), nil
        }
    }

    if err := scanner.Err(); err != nil {
        return "", err
    }

    return "", fmt.Errorf(key," not found in file")
}

func setValue(filename string,key string,value string) error {
	file, err := os.Open(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	lines := []string{}
	for scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, key) {
			line = key + "=" + value
		}
		lines = append(lines, line)
	}

	if err := scanner.Err(); err != nil {
		return err
	}

	if err := os.WriteFile(filename, []byte(strings.Join(lines, "\n")), 0644); err != nil {
		return err
	}

	return nil
}

func main() {
	var lastFilename string
	var lastCmd *exec.Cmd
	if (!fileExists("TcpdumpWrap")) {
		info := getDeviceInfo()
		fmt.Println("Device Info:", info)
	}
	lastFilename,err := getValue("TcpdumpWrap","LASTFILE")
	if err != nil {
		log.Println("Failed to get last file:", err)
	}
	if (!fileExists(lastFilename)) {
		log.Println("Last file not found:", lastFilename)
	}else{
		log.Println("Last file:", lastFilename)
		/// send all files in /tmp to RabbitMQ
	}

	for {

		timestamp := time.Now().Format("20060102-150405")
		filename := filepath.Join(os.TempDir(), fmt.Sprintf("capture-%s.pcap", timestamp))

		cmd, err := startPacketCapture(filename)
		if err != nil {
			log.Fatal("Failed to start capture:", err)
		}

		if lastCmd != nil {
			previousCmd := lastCmd
			previousFilename := lastFilename
			go func() {
				time.Sleep(1 * time.Second)
				previousCmd.Process.Kill()
				fmt.Println("Sending to RabbitMQ")
				err := sendToRabbitMQ("123", "testQueue", "amqp://guest:guest@localhost:5672/", previousFilename)
				if err != nil {
					log.Fatal("Failed to send to RabbitMQ:", err.Error())
				}

			}()
		}

		lastCmd = cmd
		lastFilename = filename

		log.Println("Started new capture:", filename)
		time.Sleep(5 * time.Second)
	}
}
