import { useEffect, useState } from "react";
import api from "../services/api";
import ChatHistory from "../components/ChatHistory";
import ChatSidebar from "../components/ChatSidebar";
import SourceCitations from "../components/SourceCitations";
import SuggestedQuestions from "../components/SuggestedQuestions";
import "./Chat.css";

const suggestedQuestions = [
  "Summarize this document",
  "What are the key points?",
  "List the important dates and figures",
  "What conclusions does this document make?",
];

function Chat() {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadChatData = async () => {
      try {
        const token = localStorage.getItem("token");
        const headers = { Authorization: `Bearer ${token}` };

        const [documentsResponse, chatsResponse] = await Promise.all([
          api.get("/documents/", { headers }),
          api.get("/chat/sessions", { headers }),
        ]);

        setDocuments(documentsResponse.data);
        setHistory(chatsResponse.data);

        if (documentsResponse.data.length > 0) {
          setSelectedDocument(documentsResponse.data[0].id);
        }

        if (chatsResponse.data.length > 0) {
          setActiveChatId(chatsResponse.data[0].id);
          setMessages(chatsResponse.data[0].messages || []);
        }
      } catch (error) {
        console.log(error);
      }
    };

    loadChatData();
  }, []);

  const saveMessagesToHistory = (
    nextMessages,
    title,
    chatId = activeChatId,
  ) => {
    setHistory((previous) =>
      previous.map((chat) =>
        chat.id === chatId
          ? {
              ...chat,
              title: title || chat.title,
              messages: nextMessages,
            }
          : chat,
      ),
    );
  };

  const createChatSession = async () => {
    const token = localStorage.getItem("token");
    const response = await api.post(
      "/chat/sessions",
      { document_id: selectedDocument ? Number(selectedDocument) : null },
      { headers: { Authorization: `Bearer ${token}` } },
    );

    return response.data;
  };

  const handleNewChat = async () => {
    if (loading) {
      return;
    }

    try {
      const chat = await createChatSession();

      setHistory((previous) => [chat, ...previous]);
      setActiveChatId(chat.id);
      setMessages(chat.messages || []);
      setQuestion("");
    } catch (error) {
      console.log(error);
    }
  };

  const handleDeleteChat = async (chatId) => {
    try {
      const token = localStorage.getItem("token");

      await api.delete(`/chat/sessions/${chatId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setHistory((previous) => previous.filter((chat) => chat.id !== chatId));

      if (chatId === activeChatId) {
        setActiveChatId(null);
        setMessages([]);
      }
    } catch (error) {
      console.log(error);
    }
  };

  const handleSelectChat = (chatId) => {
    const chat = history.find((item) => item.id === chatId);

    if (!chat || chatId === activeChatId || loading) {
      return;
    }

    setActiveChatId(chatId);
    setMessages(chat.messages || []);
    setMessages([]);
    setQuestion("");
  };

  const handleAsk = async (e) => {
    e.preventDefault();

    if (!question.trim() || !selectedDocument || loading) {
      return;
    }

    const userQuestion = question;

    const messagesWithQuestion = [
      ...messages,
      {
        role: "user",
        text: userQuestion,
      },
    ];

    setMessages(messagesWithQuestion);
    saveMessagesToHistory(messagesWithQuestion, userQuestion);

    setQuestion("");
    setLoading(true);

    try {
      const token = localStorage.getItem("token");
      let chatId = activeChatId;

      if (!chatId) {
        const chat = await createChatSession();
        chatId = chat.id;
        setHistory((previous) => [chat, ...previous]);
        setActiveChatId(chat.id);
      }

      const response = await api.post(
        "/chat/ask",
        {
          question: userQuestion,
          document_id: Number(selectedDocument),
          chat_id: chatId,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      const nextMessages = [
        ...messagesWithQuestion,
        {
          role: "assistant",
          text: response.data.answer,
          sources: response.data.sources || [],
        },
      ];

      setMessages(nextMessages);
      saveMessagesToHistory(nextMessages, userQuestion, chatId);
    } catch (error) {
      const nextMessages = [
        ...messagesWithQuestion,
        {
          role: "assistant",
          text: error.response?.data?.detail || "Something went wrong.",
          sources: [],
        },
      ];

      setMessages(nextMessages);
      saveMessagesToHistory(nextMessages, userQuestion, activeChatId);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-page">
      <div className="chat-header">
        <div>
          <h1>DocPilot-AI</h1>
          <p>Chat with your documents</p>
        </div>

        <div className="document-selector">
          <span>Document</span>

          <select
            value={selectedDocument}
            onChange={(e) => setSelectedDocument(e.target.value)}
          >
            {documents.map((document) => (
              <option key={document.id} value={document.id}>
                {document.filename}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="chat-layout">
        <ChatSidebar onNewChat={handleNewChat}>
          <ChatHistory
            history={history}
            activeChatId={activeChatId}
            onSelectChat={handleSelectChat}
            onDeleteChat={handleDeleteChat}
          />
        </ChatSidebar>

        <div className="chat-container">
          <div className="messages">
            {messages.length === 0 && (
              <div>
                <div className="empty-chat">
                  <div className="empty-icon">Doc AI</div>

                  <h2>Ask your document anything</h2>

                  <p>Select a document and ask questions about its content.</p>
                </div>

                <SuggestedQuestions
                  questions={suggestedQuestions}
                  onSelect={setQuestion}
                  disabled={!selectedDocument || loading}
                />
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`message-row ${
                  message.role === "user" ? "user-row" : "ai-row"
                }`}
              >
                <div
                  className={`message ${
                    message.role === "user" ? "user-message" : "ai-message"
                  }`}
                >
                  <div className="message-label">
                    {message.role === "user" ? "You" : "DocPilot AI"}
                  </div>

                  <div className="message-text">{message.text}</div>

                  {message.role === "assistant" && (
                    <SourceCitations sources={message.sources} />
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="message-row ai-row">
                <div className="message ai-message">
                  <div className="message-label">DocPilot AI</div>

                  <div className="typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <form className="chat-input-area" onSubmit={handleAsk}>
            <input
              type="text"
              placeholder="Ask something about your document..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={loading}
            />

            <button type="submit" disabled={loading || !question.trim()}>
              {loading ? "..." : "Ask"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Chat;
