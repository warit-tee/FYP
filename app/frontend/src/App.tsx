import './App.css'
import { Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Home from './components/Home'
import EssayInputCard from './components/EssayInputCard'

function App() {
  return (
    <>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/input" element={<EssayInputCard />} />
      </Routes>
    </>
  )
}

export default App