function ChatHistory({ history, activeChatId, onSelectChat, onDeleteChat }) {
  return (
    <div className="chat-history">
      <div className="chat-history-label">Recent chats</div>

      {history.length === 0 ? (
        <p className="chat-history-empty">
          Your conversations will appear here.
        </p>
      ) : (
        history.map((chat) => (
          <div className="chat-history-item-row" key={chat.id}>
            <button
              className={`chat-history-item ${
                chat.id === activeChatId ? "active" : ""
              }`}
              type="button"
              onClick={() => onSelectChat(chat.id)}
            >
              <span className="chat-history-title">{chat.title}</span>
              <span className="chat-history-meta">
                {chat.messages.length} messages
              </span>
            </button>

            <button
              className="delete-chat-button"
              type="button"
              title="Delete chat"
              aria-label={`Delete ${chat.title}`}
              onClick={() => onDeleteChat(chat.id)}
            >
              x
            </button>
          </div>
        ))
      )}
    </div>
  );
}

export default ChatHistory;
