import { Route, Routes } from "react-router-dom";
import { BacktestPage } from "./pages/BacktestPage";
import { LandingPage } from "./pages/LandingPage";
import "./App.css";

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/backtest/:btId" element={<BacktestPage />} />
    </Routes>
  );
}

export default App;
