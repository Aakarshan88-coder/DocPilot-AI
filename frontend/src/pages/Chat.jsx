import { useEffect, useState } from "react";
import api from "../services/api";
import "./Chat.css";

function Chat() {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const getDocuments = async () => {
    try {
      const token = localStorage.getItem("token");

      const response = await api.get("/documents/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setDocuments(response.data);

      if (response.data.length > 0) {
        setSelectedDocument(response.data[0].id);
      }
    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    getDocuments();
  }, []);

  const handleAsk = async (e) => {
    e.preventDefault();

    if (!question.trim() || !selectedDocument || loading) {
      return;
    }

    const userQuestion = question;

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        text: userQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const token = localStorage.getItem("token");

      const response = await api.post(
        "/chat/ask",
        {
          question: userQuestion,
          document_id: Number(selectedDocument),
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text: response.data.answer,
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          text:
            error.response?.data?.detail ||
            "Something went wrong.",
        },
      ]);
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
            onChange={(e) =>
              setSelectedDocument(e.target.value)
            }
          >
            {documents.map((document) => (
              <option
                key={document.id}
                value={document.id}
              >
                {document.filename}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="chat-container">

        <div className="messages">

          {messages.length === 0 && (
            <div className="empty-chat">
              <div className="empty-icon">Doc AI</div>

              <h2>Ask your document anything</h2>

              <p>
                Select a document and ask questions about
                its content.
              </p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`message-row ${
                message.role === "user"
                  ? "user-row"
                  : "ai-row"
              }`}
            >
              <div
                className={`message ${
                  message.role === "user"
                    ? "user-message"
                    : "ai-message"
                }`}
              >
                <div className="message-label">
                  {message.role === "user"
                    ? "You"
                    : "DocPilot AI"}
                </div>

                <div className="message-text">
                  {message.text}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="message-row ai-row">
              <div className="message ai-message">
                <div className="message-label">
                  DocPilot AI
                </div>

                <div className="typing">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}

        </div>

        <form
          className="chat-input-area"
          onSubmit={handleAsk}
        >
          <input
            type="text"
            placeholder="Ask something about your document..."
            value={question}
            onChange={(e) =>
              setQuestion(e.target.value)
            }
            disabled={loading}
          />

          <button
            type="submit"
            disabled={loading || !question.trim()}
          >
            {loading ? "..." : "Ask"}
          </button>
        </form>

      </div>
    </div>
  );
}

export default Chat;