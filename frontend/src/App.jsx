/**
 * Main App component with routing configuration.
 * 
 * This component:
 * - Sets up React Router for client-side navigation
 * - Defines routes: / (PlayerList) and /players/:slug (PlayerDetail)
 * - Provides layout structure (header, navigation, etc.) if needed
 * - Handles global app state or context providers
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import PlayerList from './pages/PlayerList';
import PlayerDetail from './pages/PlayerDetail';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen">
        {/* Optional: Add header/navigation here */}
        <main>
          <Routes>
            <Route path="/" element={<PlayerList />} />
            <Route path="/players/:slug" element={<PlayerDetail />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;