import './App.css'
import { Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Home from './components/Home'
import ResultCard from './components/ResultCard'
import EssayInputCard from './components/EssayInputCard'

function App() {
  return (
    <>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/input" element={<EssayInputCard />} />
        <Route path="/results" element={<ResultCard />} />
      </Routes>
    </>
  )
}

export default App