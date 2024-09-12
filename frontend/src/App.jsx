import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header>
        <h1>Data Dashboard</h1>
      </header>

      <main>
        {/* Plotting Section */}
        <section className="plotting">
          <h2>Plotting</h2>
          <div className="plot-area">
            {/* Plotting content will go here */}
            <p>This is the plotting section.</p>
          </div>
        </section>

        {/* Statistics Section */}
        <section className="statistics">
          <h2>Statistics</h2>
          <div className="statistics-area">
            {/* Statistics content will go here */}
            <p>This is the statistics section.</p>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
