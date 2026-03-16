import { useNavigate } from "react-router-dom";
import "./Home.css";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      <div className="overlay">
        <h1>SMART SCORE AI</h1>
        <p>
          AI-powered Topic Difficulty Prediction System for Competitive Exams
        </p>

        <div className="button-group">
          <button onClick={() => navigate("/student")}>
            🎓 Student Portal
          </button>

          <button onClick={() => navigate("/teacher")}>
            👩‍🏫 Teacher Portal
          </button>
        </div>

        <footer>© 2026 Smart Score AI</footer>
      </div>
    </div>
  );
}