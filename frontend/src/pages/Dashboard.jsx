import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import "./Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();
  const handleLogout = () => {
  localStorage.removeItem("token");
  navigate("/login");
};
  const [user, setUser] = useState(null);

  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [uploading, setUploading] = useState(false);

  const [documents, setDocuments] = useState([]);
  const [documentsLoading, setDocumentsLoading] = useState(false);

  const [deletingId, setDeletingId] = useState(null);


  // =========================
  // Load User Profile
  // =========================

  const getUser = async () => {
    try {
      const token = localStorage.getItem("token");

      const response = await api.get("/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setUser(response.data);
    } catch (error) {
      console.log(error);

      setMessage(
        error.response?.data?.detail || "Unable to load profile"
      );
    }
  };


  // =========================
  // Upload Document
  // =========================

  const handleUpload = async () => {
    if (!file) {
      setMessage("Please select a PDF");
      return;
    }

    try {
      setUploading(true);
      setMessage("");

      const token = localStorage.getItem("token");

      const formData = new FormData();

      formData.append("file", file);

      const response = await api.post(
        "/documents/upload",
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setMessage(
        `Uploaded successfully: ${response.data.filename}`
      );

      setFile(null);

      getDocuments();

    } catch (error) {

      setMessage(
        error.response?.data?.detail ||
        "Upload failed"
      );

    } finally {
      setUploading(false);
    }
  };


  // =========================
  // Load Documents
  // =========================

  const getDocuments = async () => {
    try {
      setDocumentsLoading(true);

      const token = localStorage.getItem("token");

      const response = await api.get(
        "/documents/",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setDocuments(response.data);

    } catch (error) {

      console.log(error);

      setMessage(
        error.response?.data?.detail ||
        "Unable to load documents"
      );

    } finally {
      setDocumentsLoading(false);
    }
  };


  // =========================
  // Delete Document
  // =========================

  const handleDelete = async (documentId) => {

    const confirmed = window.confirm(
      "Are you sure you want to delete this document?"
    );

    if (!confirmed) {
      return;
    }

    try {

      setDeletingId(documentId);
      setMessage("");

      const token = localStorage.getItem("token");

      await api.delete(
        `/documents/${documentId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setMessage(
        "Document deleted successfully"
      );

      getDocuments();

    } catch (error) {

      console.log(error);

      setMessage(
        error.response?.data?.detail ||
        "Unable to delete document"
      );

    } finally {

      setDeletingId(null);

    }
  };


  // =========================
  // Open Chat
  // =========================

  const openChat = (documentId = null) => {

    if (documentId) {

      navigate("/chat", {
        state: {
          documentId: documentId,
        },
      });

    } else {

      navigate("/chat");

    }
  };


  return (
    <div className="dashboard-page">


      {/* =========================
          Header
      ========================= */}

      <header className="dashboard-header">

        <div className="dashboard-brand">

          <div className="dashboard-brand-icon">
            D
          </div>

          <div>

            <h1>
              DocPilot-AI
            </h1>

            <p>
              Document Intelligence Workspace
            </p>

          </div>

        </div>


        <button
          className="chat-button"
          onClick={() => openChat()}
        >
          Open AI Chat
        </button>
      <button className="logout-button" onClick={handleLogout}>
       Logout
      </button>
      </header>



      {/* =========================
          Main Content
      ========================= */}

      <main className="dashboard-content">


        {/* =========================
            Welcome
        ========================= */}

        <section className="welcome-section">

          <div>

            <p className="welcome-label">
              DASHBOARD
            </p>

            <h2>

              Welcome back
              {user?.name
                ? `, ${user.name}`
                : ""}

            </h2>

            <p>
              Upload your documents and ask
              DocPilot-AI questions about them.
            </p>

          </div>


          {!user && (

            <button
              className="profile-button"
              onClick={getUser}
            >
              Load Profile
            </button>

          )}

        </section>



        {/* =========================
            Profile
        ========================= */}

        {user && (

          <section className="profile-card">

            <div className="profile-avatar">

              {user.name
                ?.charAt(0)
                ?.toUpperCase() || "U"}

            </div>


            <div>

              <h3>
                {user.name}
              </h3>

              <p>
                {user.email}
              </p>

            </div>

          </section>

        )}



        {/* =========================
            Statistics
        ========================= */}

        <section className="stats-grid">


          <div className="stat-card">

            <div className="stat-icon">
              D
            </div>

            <div>

              <span>
                Total Documents
              </span>

              <strong>
                {documents.length}
              </strong>

            </div>

          </div>


          <div className="stat-card">

            <div className="stat-icon">
              AI
            </div>

            <div>

              <span>
                AI Assistant
              </span>

              <strong>
                Ready
              </strong>

            </div>

          </div>


          <div className="stat-card">

            <div className="stat-icon">
              PDF
            </div>

            <div>

              <span>
                Supported Format
              </span>

              <strong>
                PDF
              </strong>

            </div>

          </div>


        </section>



        {/* =========================
            Upload
        ========================= */}

        <section className="upload-card">


          <div className="section-heading">

            <div>

              <h2>
                Upload Document
              </h2>

              <p>
                Add a PDF to start asking
                questions about its content.
              </p>

            </div>

          </div>



          <div className="upload-area">

            <div className="upload-icon">
              ↑
            </div>


            <h3>

              {file
                ? file.name
                : "Choose a PDF document"}

            </h3>


            <p>
              Maximum file size: 10 MB
            </p>


            <label className="choose-file-button">

              Choose PDF

              <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={(e) =>
                  setFile(e.target.files[0])
                }
              />

            </label>


            {file && (

              <button
                className="upload-button"
                onClick={handleUpload}
                disabled={uploading}
              >

                {uploading
                  ? "Uploading..."
                  : "Upload Document"}

              </button>

            )}

          </div>



          {/* Message */}

          {message && (

            <div
              className={
                message
                  .toLowerCase()
                  .includes("success")
                  ? "upload-message success"
                  : "upload-message error"
              }
            >

              {message}

            </div>

          )}

        </section>



        {/* =========================
            Documents
        ========================= */}

        <section className="documents-card">


          <div className="documents-heading">

            <div>

              <h2>
                Your Documents
              </h2>

              <p>
                Documents uploaded to
                your workspace.
              </p>

            </div>


            <button
              className="refresh-button"
              onClick={getDocuments}
              disabled={documentsLoading}
            >

              {documentsLoading
                ? "Loading..."
                : "Load Documents"}

            </button>

          </div>



          {/* Documents List */}

          <div className="documents-list">


            {documentsLoading ? (

              <div className="documents-empty">

                <p>
                  Loading your documents...
                </p>

              </div>


            ) : documents.length === 0 ? (

              <div className="documents-empty">

                <div className="empty-document-icon">
                  D
                </div>

                <h3>
                  No documents yet
                </h3>

                <p>
                  Upload your first PDF to
                  start using DocPilot-AI.
                </p>

              </div>


            ) : (

              documents.map((document) => (

                <div
                  className="document-item"
                  key={document.id}
                >


                  {/* Document Information */}

                  <div className="document-info">

                    <div className="document-icon">
                      PDF
                    </div>


                    <div>

                      <h3>
                        {document.filename}
                      </h3>

                      <p>
                        Document ID: {document.id}
                      </p>

                    </div>

                  </div>



                  {/* Document Actions */}

                  <div className="document-actions">


                    <button
                      className="document-chat-button"
                      onClick={() =>
                        openChat(document.id)
                      }
                    >
                      Ask AI
                    </button>


                    <button
                      className="document-delete-button"
                      onClick={() =>
                        handleDelete(document.id)
                      }
                      disabled={
                        deletingId === document.id
                      }
                    >

                      {deletingId === document.id
                        ? "Deleting..."
                        : "Delete"}

                    </button>


                  </div>


                </div>

              ))

            )}

          </div>

        </section>


      </main>

    </div>
  );
}

export default Dashboard;