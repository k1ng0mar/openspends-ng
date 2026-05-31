import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Header from './components/layout/Header'
import Footer from './components/layout/Footer'
import HomePage from './pages/Home'
import MdaDetailPage from './pages/MdaDetail'
import ProjectListPage from './pages/ProjectList'
import AnalyticsPage from './pages/Analytics'
import MapPage from './pages/Map'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-cream-page text-ink-body flex flex-col font-body">
        <Header />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/mdas/:id" element={<MdaDetailPage />} />
            <Route path="/projects" element={<ProjectListPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/map" element={<MapPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  )
}
