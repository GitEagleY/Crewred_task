import { useState, useEffect } from 'react';
import type { Project, Place } from './types'; 
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [newProjectName, setNewProjectName] = useState('');
  const [newPlaceId, setNewPlaceId] = useState('');
  const [loading, setLoading] = useState(false);
  const [isEditingProject, setIsEditingProject] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await fetch(`${API_URL}/projects`);
      const data = await res.json();
      setProjects(data);
    } catch (err) { console.error(err); }
  };

  const createProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;
    const res = await fetch(`${API_URL}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: newProjectName })
    });
    if (res.ok) {
      setNewProjectName('');
      fetchProjects();
    }
  };

  const selectProject = async (id: number) => {
    const res = await fetch(`${API_URL}/projects/${id}`);
    const data = await res.json();
    setSelectedProject(data);
    setIsEditingProject(false);
  };

  const deleteProject = async (id: number) => {
    if (!window.confirm("Delete this entire trip?")) return;
    const res = await fetch(`${API_URL}/projects/${id}`, { method: 'DELETE' });
    if (res.ok) {
      setSelectedProject(null);
      fetchProjects();
    } else {
      const err = await res.json();
      alert(err.detail); // Shows "Cannot delete - has visited places"
    }
  };

  const updateProject = async () => {
    if (!selectedProject) return;
    const res = await fetch(`${API_URL}/projects/${selectedProject.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        name: selectedProject.name, 
        description: selectedProject.description 
      })
    });
    if (res.ok) {
      setIsEditingProject(false);
      fetchProjects();
    }
  };

  const addPlace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProject || !newPlaceId) return;
    setLoading(true);
    const res = await fetch(`${API_URL}/projects/${selectedProject.id}/places`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ external_api_id: newPlaceId })
    });
    if (res.ok) {
      setNewPlaceId('');
      selectProject(selectedProject.id);
    } else {
      const err = await res.json();
      alert(err.detail);
    }
    setLoading(false);
  };

  const deletePlace = async (placeId: number) => {
    if (!selectedProject) return;
    const res = await fetch(`${API_URL}/projects/${selectedProject.id}/places/${placeId}`, {
      method: 'DELETE'
    });
    if (res.ok) selectProject(selectedProject.id);
  };

  const toggleVisited = async (place: Place) => {
    if (!selectedProject) return;
    const res = await fetch(`${API_URL}/projects/${selectedProject.id}/places/${place.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ visited: !place.visited })
    });
    if (res.ok) {
      await selectProject(selectedProject.id);
      fetchProjects();
    }
  };

  return (
    <div className="app-container">
      <nav className="sidebar">
        <div className="sidebar-header">
          <h2>My Trips</h2>
          <form onSubmit={createProject} className="quick-add">
            <input 
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              placeholder="Trip name..."
            />
            <button type="submit" className="btn-add">+</button>
          </form>
        </div>
        
        <div className="project-list">
          {projects.map(p => (
            <div 
              key={p.id} 
              className={`project-item ${selectedProject?.id === p.id ? 'active' : ''}`}
              onClick={() => selectProject(p.id)}
            >
              <span>{p.name}</span>
              {p.completed && <span className="badge">Done</span>}
            </div>
          ))}
        </div>
      </nav>

      <main className="content">
        {selectedProject ? (
          <div className="project-view">
            <header className="main-header">
              <div className="header-info">
                {isEditingProject ? (
                  <div className="edit-project-form">
                    <input 
                      className="edit-title"
                      value={selectedProject.name}
                      onChange={e => setSelectedProject({...selectedProject, name: e.target.value})}
                    />
                    <textarea 
                      placeholder="Add a description..."
                      value={selectedProject.description || ''}
                      onChange={e => setSelectedProject({...selectedProject, description: e.target.value})}
                    />
                    <button onClick={updateProject}>Save Changes</button>
                  </div>
                ) : (
                  <>
                    <h1>{selectedProject.name}</h1>
                    <p>{selectedProject.description || "No description set"}</p>
                    <div className="header-actions">
                      <button className="btn-outline" onClick={() => setIsEditingProject(true)}>Edit Details</button>
                      <button className="btn-danger" onClick={() => deleteProject(selectedProject.id)}>Delete Trip</button>
                    </div>
                  </>
                )}
              </div>
            </header>

            <section className="places-section">
              <div className="section-title">
                <h3>Places to Visit</h3>
                <form onSubmit={addPlace} className="add-place-inline">
                  <input 
                    value={newPlaceId}
                    onChange={(e) => setNewPlaceId(e.target.value)}
                    placeholder="Art Institute ID..."
                    disabled={loading}
                  />
                  <button type="submit" disabled={loading}>
                    {loading ? 'Adding...' : 'Add Artwork'}
                  </button>
                </form>
              </div>

              <div className="grid">
                {selectedProject.places.map(place => (
                  <div key={place.id} className={`card ${place.visited ? 'visited' : ''}`}>
                    <div className="card-header">
                       <h4>{place.external_api_title}</h4>
                       <button className="btn-close" onClick={() => deletePlace(place.id)}>×</button>
                    </div>
                    <a href={place.external_api_url || '#'} target="_blank" rel="noreferrer">View Artwork ↗</a>
                    <div className="card-actions">
                      <button className={`btn-visit ${place.visited ? 'is-visited' : ''}`} onClick={() => toggleVisited(place)}>
                        {place.visited ? '✓ Visited' : 'Mark Visited'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>
        ) : (
          <div className="placeholder">
            <div className="placeholder-icon">🌍</div>
            <h2>Select a trip from the sidebar to begin planning.</h2>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;