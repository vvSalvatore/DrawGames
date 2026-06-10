import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import Home from "./pages/Home";
import ComingSoon from "./pages/ComingSoon";
import GameDetail from "./pages/GameDetail";
import SourceDetail, { SourcesList } from "./pages/Sources";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/library" element={<Home />} />
          <Route path="/coming-soon" element={<ComingSoon />} />
          <Route path="/game/:id" element={<GameDetail />} />
          <Route path="/sources" element={<SourcesList />} />
          <Route path="/sources/:id" element={<SourceDetail />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <Toaster position="top-center" theme="dark" />
      </BrowserRouter>
    </div>
  );
}

export default App;
