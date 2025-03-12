# LM Studio Chat

A desktop application that enables users to have interactive conversations with local language models through LM Studio's API. The application supports single-person conversations with historical figures, scientists, artists, and other notable personalities, as well as simulated conversations between two historical figures.

![LM Studio Chat](https://via.placeholder.com/800x500?text=LM+Studio+Chat+Screenshot)

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Single Chat Mode](#single-chat-mode)
  - [Dual Chat Mode](#dual-chat-mode)
- [Dictionary Management](#dictionary-management)
- [API Configuration](#api-configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Single Chat Mode**: Converse with a historical figure, scientist, artist, or any notable personality
- **Dual Chat Mode**: Watch two historical figures have a conversation based on a context you provide
- **Customizable Dictionary**: Load, save, and customize the list of people available for conversations
- **Conversation Management**: Save conversations to review or share later
- **Non-blocking UI**: API calls run in the background, keeping the interface responsive
- **Local AI Integration**: Works with LM Studio's local API server

## Requirements

- Python 3.6 or higher
- PyQt5
- Requests library
- LM Studio running locally with API server enabled

## Installation

1. Clone this repository or download the source code.

```bash
git clone https://github.com/yourusername/lm-studio-chat.git
cd lm-studio-chat
```

2. Install the required dependencies:

```bash
pip install pyqt5 requests
```

3. Launch LM Studio and start the server:
   - Open LM Studio
   - Load your preferred language model
   - Click on "Local Server" in the sidebar
   - Enable the server by clicking the power button

4. Run the application:

```bash
python LM_Studio_Chat.py
```

## Usage

### Single Chat Mode

1. Select a category from the dropdown menu or type a custom figure name
2. Choose a specific figure from the selected category
3. Click "Start Conversation" to begin
4. Type your message in the input box and click "Send"
5. The figure will respond based on their historical context and personality

### Dual Chat Mode

1. Select two different figures from the dropdown menus
2. Enter an initial context for their conversation (e.g., "Debate the ethics of AI")
3. Click "Start Conversation" to begin the automated exchange
4. Watch as the two historical figures converse with each other
5. Click "Stop Conversation" at any time to end the exchange
6. Use "Save Conversation" to export the dialogue as a text file

## Dictionary Management

The application uses a dictionary file to organize available figures into categories. By default, it includes various categories such as Presidents, Scientists, Artists, etc.

- **Default Dictionary**: The application comes with a default dictionary (FamousPeople.dict)
- **Load Dictionary**: Load a custom dictionary from a JSON file
- **Output Prompt Template**: Save the system prompts used for each figure

### Dictionary Format

The dictionary is a JSON file structured as follows:

```json
{
  "Category1": ["Person1", "Person2", "Person3"],
  "Category2": ["Person4", "Person5", "Person6"],
  "Scientists": ["Albert Einstein", "Isaac Newton", "Marie Curie"]
}
```

## API Configuration

The application is configured to connect to LM Studio's API server at `http://localhost:1234/v1/chat/completions`. If your server is running on a different port, you may need to modify the `api_url` variable in the source code.

Configuration options used for the API:
- Model: "default" (uses the currently loaded model in LM Studio)
- Temperature: 0.7 (controls creativity level)
- Max tokens: 500 (limits response length)

## Troubleshooting

### Common Issues

1. **Connection Error**: Ensure LM Studio is running and the server is enabled
2. **No Response**: Check that you have a model loaded in LM Studio
3. **UI Freezing**: If the interface becomes unresponsive, restart the application
4. **Invalid Dictionary**: If loading a custom dictionary fails, check the JSON format

### Debug Tips

- Look for error messages in the terminal or console
- Check if the API server is accessible by visiting http://localhost:1234 in your browser
- Verify your JSON dictionary file format with a JSON validator

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*Note: This application is a UI wrapper for LM Studio's API. It is not affiliated with or endorsed by LM Studio.*
