import sys
import json
import time
import os
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QComboBox, QTextEdit, QPushButton,
                             QLabel, QLineEdit, QSplitter, QFileDialog,
                             QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt, QTimer, QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QTextCharFormat, QFont

# Worker thread for API calls to prevent UI freezing
class ApiWorker(QObject):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, url, payload):
        super().__init__()
        self.url = url
        self.payload = payload
        
    @pyqtSlot()
    def run(self):
        try:
            response = requests.post(self.url, json=self.payload)
            if response.status_code == 200:
                self.finished.emit(response.json())
            else:
                self.error.emit(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            self.error.emit(f"Request failed: {str(e)}")

class LMStudioChat(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LM Studio Chat")
        self.setMinimumSize(1000, 700)

        # Default dictionary (valid JSON)
        self.default_categories = {
            "Presidents": ["George Washington", "Abraham Lincoln", "Thomas Jefferson", "Franklin D. Roosevelt",
                            "John F. Kennedy", "Theodore Roosevelt", "Ronald Reagan", "Barack Obama",
                            "Dwight D. Eisenhower", "Harry S. Truman"],
            "Scientists": ["Albert Einstein", "Isaac Newton", "Marie Curie", "Nikola Tesla", "Charles Darwin",
                            "Richard Feynman", "Galileo Galilei", "Stephen Hawking", "Neil deGrasse Tyson",
                            "Carl Sagan", "Alan Turing", "Rachel Carson", "Rosalind Franklin", "Katherine Johnson",
                            "James Watson", "Francis Crick", "Jane Goodall"],
            "Artists": ["Leonardo da Vinci", "Vincent van Gogh", "Frida Kahlo", "Pablo Picasso", "Michelangelo",
                        "Claude Monet", "Salvador Dalí", "Georgia O'Keeffe", "Andy Warhol", "Rembrandt", "Banksy",
                        "Jean-Michel Basquiat"],
            "Writers": ["William Shakespeare", "Jane Austen", "Mark Twain", "Ernest Hemingway", "Virginia Woolf",
                        "Leo Tolstoy", "Oscar Wilde", "Maya Angelou", "Gabriel García Márquez", "Franz Kafka",
                        "Emily Dickinson", "Edgar Allan Poe", "Toni Morrison", "George Orwell", "J.K. Rowling",
                        "Haruki Murakami"],
            "Philosophers": ["Socrates", "Plato", "Aristotle", "Confucius", "Friedrich Nietzsche", "René Descartes",
                            "Immanuel Kant", "Jean-Jacques Rousseau", "John Locke", "Simone de Beauvoir",
                            "Jean-Paul Sartre", "Karl Marx", "Hannah Arendt", "Bertrand Russell",
                            "Michel Foucault"],
            "Inventors": ["Thomas Edison", "Alexander Graham Bell", "Steve Jobs", "Ada Lovelace",
                        "Johannes Gutenberg", "Leonardo da Vinci", "James Watt", "Grace Hopper", "Hedy Lamarr",
                        "Wright Brothers", "Marie Van Brittan Brown"],
            "Musicians": ["Wolfgang Amadeus Mozart", "Ludwig van Beethoven", "Johann Sebastian Bach",
                        "Freddie Mercury", "John Lennon", "Elvis Presley", "David Bowie", "Bob Dylan",
                        "Michael Jackson", "Prince", "Madonna", "Aretha Franklin", "Nina Simone",
                        "Louis Armstrong", "Bob Marley", "Jimi Hendrix"],
            "Athletes": ["Muhammad Ali", "Michael Jordan", "Pelé", "Serena Williams", "Babe Ruth", "Usain Bolt",
                        "Wayne Gretzky", "Jesse Owens", "Billie Jean King", "Michael Phelps", "Tiger Woods",
                        "Simone Biles", "Kobe Bryant", "Jackie Robinson", "Wilma Rudolph"],
            "Political Leaders": ["Mahatma Gandhi", "Winston Churchill", "Nelson Mandela", "Margaret Thatcher",
                                    "Martin Luther King Jr.", "Cleopatra", "Queen Elizabeth I", "Queen Victoria",
                                    "Catherine the Great", "Angela Merkel", "Benazir Bhutto", "Indira Gandhi",
                                    "Golda Meir", "Eleanor Roosevelt"],
            "Activists": ["Malcolm X", "Rosa Parks", "Emmeline Pankhurst", "Harvey Milk", "Gloria Steinem",
                        "Malala Yousafzai", "Cesar Chavez", "Greta Thunberg", "Susan B. Anthony", "Harriet Tubman",
                        "Helen Keller", "Desmond Tutu", "Rigoberta Menchú", "Betty Friedan"],
            "Military": ["Napoleon Bonaparte", "Alexander the Great", "Sun Tzu", "Genghis Khan", "Julius Caesar",
                        "Hannibal Barca", "Joan of Arc", "George S. Patton", "Erwin Rommel",
                        "Dwight D. Eisenhower", "Admiral Yi Sun-sin", "Spartacus", "Boudicca", "Sitting Bull"],
            "Entrepreneurs": ["Henry Ford", "Elon Musk", "Bill Gates", "Andrew Carnegie", "Oprah Winfrey",
                            "Jeff Bezos", "Warren Buffett", "Steve Jobs", "Richard Branson", "Arianna Huffington",
                            "Mark Zuckerberg", "Coco Chanel", "Walt Disney", "John D. Rockefeller",
                            "Madam C.J. Walker"],
            "Explorers": ["Christopher Columbus", "Marco Polo", "Amelia Earhart", "Neil Armstrong",
                        "Jacques Cousteau", "Roald Amundsen", "Edmund Hillary", "Tenzing Norgay", "Sacagawea",
                        "Ibn Battuta", "Captain James Cook", "Lewis and Clark", "David Livingstone", "Zheng He",
                        "Matthew Henson", "Ernest Shackleton"]
        }

        self.current_dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FamousPeople.dict")
        if not os.path.exists(self.current_dict_path):
            self.save_dictionary(self.current_dict_path, self.default_categories)
        self.categories = self.load_dictionary(self.current_dict_path)
        self.update_all_figures()

        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # First tab: Single Chat
        self.tab1 = QWidget()
        self.tab1_layout = QHBoxLayout(self.tab1)
        self.tabs.addTab(self.tab1, "Single Chat")
        self.setup_single_chat_tab()

        # Second tab: Dual Chat
        self.tab2 = QWidget()
        self.tab2_layout = QVBoxLayout(self.tab2)
        self.tabs.addTab(self.tab2, "Dual Chat")
        self.setup_dual_chat_tab()

        # Initialize current figure
        self.current_figure = None
        self.conversation_history = []
        self.figure_prompts = {}
        self.update_figure_prompts()
        self.conversation_active = False
        self.api_url = "http://localhost:1234/v1/chat/completions"
        
        # Initialize threads list to keep references
        self.threads = []
        self.workers = []
        
        # Initialize dual chat conversation record
        self.dual_conversation_log = []

    def setup_single_chat_tab(self):
        # Splitter for left and right panes
        splitter = QSplitter(Qt.Horizontal)

        # Left pane for selection controls
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.setSpacing(10)

        # Dictionary management
        dict_layout = QHBoxLayout()
        self.current_dict_label = QLabel("Current Dictionary: FamousPeople.dict")
        dict_layout.addWidget(self.current_dict_label)
        left_layout.addLayout(dict_layout)

        dict_buttons_layout = QHBoxLayout()
        self.load_dict_button = QPushButton("Load Dictionary")
        self.load_dict_button.clicked.connect(self.load_dictionary_dialog)
        dict_buttons_layout.addWidget(self.load_dict_button)

        self.output_prompt_button = QPushButton("Output Prompt Template")
        self.output_prompt_button.clicked.connect(self.output_prompt_template)
        dict_buttons_layout.addWidget(self.output_prompt_button)
        left_layout.addLayout(dict_buttons_layout)

        # Category selection
        left_layout.addWidget(QLabel("Select Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(sorted(self.categories.keys()))
        self.category_combo.currentTextChanged.connect(self.update_figure_combo)
        left_layout.addWidget(self.category_combo)

        # Figure selection
        left_layout.addWidget(QLabel("Select a figure:"))
        self.figure_combo = QComboBox()
        self.update_figure_combo(self.category_combo.currentText())
        left_layout.addWidget(self.figure_combo)

        # Custom figure input
        left_layout.addWidget(QLabel("Or Enter Custom Figure:"))
        self.custom_figure = QLineEdit()
        left_layout.addWidget(self.custom_figure)

        # Selection button
        self.select_button = QPushButton("Start Conversation")
        self.select_button.clicked.connect(self.start_conversation)
        left_layout.addWidget(self.select_button)
        left_layout.addStretch()

        # Right pane for chat interface
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        right_layout.addWidget(self.chat_display)

        # User input area
        self.user_input = QTextEdit()
        self.user_input.setMaximumHeight(100)
        self.user_input.setPlaceholderText("Type your message here...")
        right_layout.addWidget(self.user_input)

        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        right_layout.addWidget(self.send_button)

        # Add both panes to the splitter
        splitter.addWidget(left_pane)
        splitter.addWidget(right_pane)

        # Set initial splitter sizes (30% left, 70% right)
        splitter.setSizes([300, 700])

        # Set the splitter as the central layout for tab1
        self.tab1_layout.addWidget(splitter)

    def setup_dual_chat_tab(self):
        # Control panel for dropdowns and buttons
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        
        # Dropdowns layout
        dropdown_layout = QHBoxLayout()
        
        # First figure selection
        first_figure_layout = QVBoxLayout()
        category_label1 = QLabel("Select Category 1:")
        self.category_combo1 = QComboBox()
        self.category_combo1.addItems(sorted(self.categories.keys()))
        self.category_combo1.currentTextChanged.connect(self.update_figure_combo1)
        
        figure_label1 = QLabel("Select Figure 1:")
        self.figure_combo1 = QComboBox()
        self.update_figure_combo1(self.category_combo1.currentText())
        
        first_figure_layout.addWidget(category_label1)
        first_figure_layout.addWidget(self.category_combo1)
        first_figure_layout.addWidget(figure_label1)
        first_figure_layout.addWidget(self.figure_combo1)
        dropdown_layout.addLayout(first_figure_layout)
        
        # Second figure selection
        second_figure_layout = QVBoxLayout()
        category_label2 = QLabel("Select Category 2:")
        self.category_combo2 = QComboBox()
        self.category_combo2.addItems(sorted(self.categories.keys()))
        self.category_combo2.currentTextChanged.connect(self.update_figure_combo2)
        
        figure_label2 = QLabel("Select Figure 2:")
        self.figure_combo2 = QComboBox()
        self.update_figure_combo2(self.category_combo2.currentText())
        
        second_figure_layout.addWidget(category_label2)
        second_figure_layout.addWidget(self.category_combo2)
        second_figure_layout.addWidget(figure_label2)
        second_figure_layout.addWidget(self.figure_combo2)
        dropdown_layout.addLayout(second_figure_layout)
        
        control_layout.addLayout(dropdown_layout)
        
        # Context Input
        context_layout = QVBoxLayout()
        self.context_label = QLabel("Initial Context:")
        self.context_input = QTextEdit()
        self.context_input.setMaximumHeight(100)
        self.context_input.setPlaceholderText("Enter the initial context for the conversation...")
        context_layout.addWidget(self.context_label)
        context_layout.addWidget(self.context_input)
        control_layout.addLayout(context_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Conversation")
        self.start_button.clicked.connect(self.start_dual_conversation)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Conversation")
        self.stop_button.clicked.connect(self.stop_dual_conversation)
        button_layout.addWidget(self.stop_button)
        
        self.save_dual_chat_button = QPushButton("Save Conversation")
        self.save_dual_chat_button.clicked.connect(self.save_dual_conversation)
        button_layout.addWidget(self.save_dual_chat_button)
        
        control_layout.addLayout(button_layout)
        
        # Main dual chat split layout
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(control_panel)
        
        # Single conversation display
        chat_panel = QWidget()
        chat_layout = QVBoxLayout(chat_panel)
        
        # Single conversation window
        self.dual_chat_display = QTextEdit()
        self.dual_chat_display.setReadOnly(True)
        self.dual_chat_display.setStyleSheet("font-family: Arial; font-size: 10pt; line-height: 150%;")
        chat_layout.addWidget(self.dual_chat_display)
        
        splitter.addWidget(chat_panel)
        
        # Set initial splitter sizes (30% controls, 70% chat)
        splitter.setSizes([300, 700])
        
        # Add splitter to tab layout
        self.tab2_layout.addWidget(splitter)

    def load_dictionary_dialog(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Load Dictionary", "", "Dictionary Files (*.json)")
        if file_path:
            self.current_dict_path = file_path
            self.categories = self.load_dictionary(self.current_dict_path)
            self.update_all_figures()
            self.update_figure_prompts()

            # Update all combo boxes
            for combo in [self.category_combo, self.category_combo1, self.category_combo2]:
                current_text = combo.currentText()
                combo.clear()
                combo.addItems(sorted(self.categories.keys()))
                combo.setCurrentText(current_text if current_text in self.categories else list(self.categories.keys())[0] if self.categories else "")

            self.current_dict_label.setText(f"Current Dictionary: {os.path.basename(file_path)}")

    def output_prompt_template(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Prompt Template", "", "Text Files (*.txt)",
                                                    options=options)
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    for figure, prompt in self.figure_prompts.items():
                        f.write(f"### {figure} ###\n{prompt}\n\n")
                QMessageBox.information(self, "Success", "Prompt templates exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def update_all_figures(self):
        self.all_figures = [figure for figures in self.categories.values() for figure in figures]

    def update_figure_prompts(self):
        self.figure_prompts = {figure: f"You are now roleplaying as {figure}." for category in self.categories for
                               figure in self.categories[category]}

    def update_figure_combo(self, category):
        self.figure_combo.clear()
        self.figure_combo.addItems(sorted(self.categories.get(category, [])))

    def update_figure_combo1(self, category):
        self.figure_combo1.clear()
        self.figure_combo1.addItems(sorted(self.categories.get(category, [])))

    def update_figure_combo2(self, category):
        self.figure_combo2.clear()
        self.figure_combo2.addItems(sorted(self.categories.get(category, [])))

    def start_conversation(self):
        selected_figure = self.custom_figure.text().strip() or self.figure_combo.currentText()
        self.current_figure = selected_figure
        self.conversation_history = []
        self.chat_display.clear()
        self.chat_display.append(f"Starting conversation with {self.current_figure}")
        self.get_llm_response("Please introduce yourself briefly.")

    def start_dual_conversation(self):
        # Get selected figures
        self.figure1 = self.figure_combo1.currentText()
        self.figure2 = self.figure_combo2.currentText()

        if not self.figure1 or not self.figure2:
            QMessageBox.warning(self, "Selection Error", "Please select both figures to start the conversation.")
            return

        # Get context
        self.context = self.context_input.toPlainText().strip()

        # Initialize conversation parameters
        self.conversation_active = True
        self.history1 = [{
            "role": "system",
            "content": f"You are {self.figure1}. Engage in a natural conversation with {self.figure2} about the following context: {self.context}. "
                       f"Maintain your perspective and personality. Respond directly to the last message."
        }]
        self.history2 = [{
            "role": "system",
            "content": f"You are {self.figure2}. Engage in a natural conversation with {self.figure1} about the following context: {self.context}. "
                       f"Maintain your perspective and personality. Respond directly to the last message."
        }]
    
        # Clear the dual conversation log and initialize counter for ordering
        self.dual_conversation_log = []
        self.message_counter = 0  # Track message order
        
        # Define colors for each speaker
        self.figure1_color = QColor(0, 0, 255)  # Blue for figure1
        self.figure2_color = QColor(139, 0, 0)  # Dark Red for figure2

        # Clear conversation display and show header
        self.dual_chat_display.clear()
        self.dual_chat_display.append("<h2>Conversation</h2>")
        self.dual_chat_display.append(f"<b>Context:</b> {self.context}")
        self.dual_chat_display.append("<hr>")

        # Start the conversation with an initial message from figure1
        self._send_dual_message(initiator=self.figure1, responder=self.figure2)

    def _send_dual_message(self, initiator, responder):
        if not self.conversation_active:
            return

        # Determine which history to use
        history = self.history1 if initiator == self.figure1 else self.history2

        # Create worker thread for API call
        thread = QThread()
        worker = ApiWorker(self.api_url, {
            "model": "default",
            "messages": history,
            "temperature": 0.7,
            "max_tokens": 500
        })
        
        # Keep reference to avoid garbage collection
        self.threads.append(thread)
        self.workers.append(worker)
        
        # Move worker to thread
        worker.moveToThread(thread)
        
        # Connect signals
        thread.started.connect(worker.run)
        worker.finished.connect(lambda response: self._handle_dual_response(response, initiator, responder, history))
        worker.error.connect(self.handle_dual_error)
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.finished.connect(lambda: self._cleanup_thread(thread, worker))
        
        # Start thread
        thread.start()

    def _handle_dual_response(self, response_data, initiator, responder, history):
        if not self.conversation_active:
            return
        
        llm_response = response_data["choices"][0]["message"]["content"]
        timestamp = time.time()
    
        # Increment message counter to ensure chronological order
        self.message_counter += 1

        # Update histories with timestamp
        history.append({"role": "assistant", "content": llm_response, "timestamp": timestamp})
        # Add to the other figure's history as a user message
        (self.history2 if initiator == self.figure1 else self.history1).append(
            {"role": "user", "content": llm_response, "timestamp": timestamp})
        
        # Add to dual conversation log with sequence number for guaranteed ordering
        self.dual_conversation_log.append({
            "speaker": initiator,
            "content": llm_response,
            "timestamp": timestamp,
            "sequence": self.message_counter
        })

        # Format and add the message to the display
        color = self.figure1_color if initiator == self.figure1 else self.figure2_color
        formatted_text = f"<p><b><font color='{color.name()}'>{initiator}:</font></b><br>{llm_response}</p>"
        self.dual_chat_display.append(formatted_text)
        self.dual_chat_display.verticalScrollBar().setValue(self.dual_chat_display.verticalScrollBar().maximum())

        # Continue conversation after a brief delay
        QTimer.singleShot(2500, lambda: self._send_dual_message(responder, initiator))

    def _cleanup_thread(self, thread, worker):
        # Remove references to allow garbage collection
        if thread in self.threads:
            self.threads.remove(thread)
        if worker in self.workers:
            self.workers.remove(worker)

    def handle_dual_error(self, error_msg):
        self.dual_chat_display.append(f"<p style='color: red;'>{error_msg}</p>")
        self.stop_dual_conversation()

    def stop_dual_conversation(self):
        self.conversation_active = False
        self.dual_chat_display.append("<p><b>Conversation stopped.</b></p>")

    def save_dual_conversation(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Conversation", "", "Text Files (*.txt)", options=options)
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(f"Conversation between {self.figure1} and {self.figure2}\n")
                    f.write(f"Context: {self.context}\n\n")
            
                    # Sort the conversation log by sequence number
                    sorted_log = sorted(self.dual_conversation_log, key=lambda x: x.get('sequence', x['timestamp']))
            
                    # Write the conversation in chronological order
                    for entry in sorted_log:
                        f.write(f"{entry['speaker']}: {entry['content']}\n\n")
                    
                QMessageBox.information(self, "Success", "Conversation saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save conversation: {str(e)}")

    def send_message(self):
        if not self.current_figure:
            self.chat_display.append("Please select a figure first.")
            return

        user_message = self.user_input.toPlainText().strip()
        if not user_message:
            return

        self.chat_display.append(f"You: {user_message}")
        self.user_input.clear()
        self.get_llm_response(user_message)

    def load_dictionary(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"Dictionary file not found at {path}")
            return {}
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", f"Invalid JSON format in dictionary file at {path}")
            return {}

    def save_dictionary(self, path, data):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save dictionary file: {str(e)}")

    def get_llm_response(self, prompt):
        if not self.current_figure:
            self.chat_display.append("No figure selected. Please select a figure to start a conversation.")
            return
    
        # Retrieve the figure prompt or use a default
        figure_prompt = self.figure_prompts.get(self.current_figure, f"You are {self.current_figure}.")
    
        # System prompt
        system_prompt = {"role": "system", "content": figure_prompt}
    
        # Include the user's prompt
        user_prompt = {"role": "user", "content": prompt, "timestamp": time.time()}
    
        # Append the prompts to the conversation history
        self.conversation_history.append(user_prompt)
    
        # Prepare the messages payload for the API request
        messages = [system_prompt] + self.conversation_history
        
        # Create and run the worker in a separate thread
        thread = QThread()
        worker = ApiWorker(self.api_url, {
            "model": "default", 
            "messages": messages, 
            "temperature": 0.7, 
            "max_tokens": 500
        })
        
        # Keep references
        self.threads.append(thread)
        self.workers.append(worker)
        
        # Setup the worker
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(lambda response: self._handle_single_response(response))
        worker.error.connect(lambda error: self.chat_display.append(error))
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.finished.connect(lambda: self._cleanup_thread(thread, worker))
        
        # Start thread
        thread.start()

    def _handle_single_response(self, response_data):
        llm_response = response_data["choices"][0]["message"]["content"]
        timestamp = time.time()
        
        # Append the LLM's response to the conversation history with timestamp
        self.conversation_history.append({
            "role": "assistant", 
            "content": llm_response,
            "timestamp": timestamp
        })
        
        # Display the response in the chat display
        self.chat_display.append(f"{self.current_figure}: {llm_response}")
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = LMStudioChat()
    mainWin.show()
    sys.exit(app.exec_())