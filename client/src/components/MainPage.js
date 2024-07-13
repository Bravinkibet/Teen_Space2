import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import "./Mainpage.css";
import Clubcard from "./Clubcard"

function MainPage() {
  const [clubs, setClubs] = useState([]);

  useEffect(() => {
    fetchClubs();
  }, []);

  useEffect(() => {
    console.log('Clubs state updated:', clubs);
  }, [clubs]);

  const fetchClubs = () => {
    fetch('http://localhost:5000/clubs')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Data received from server:', data);
        setClubs(data);
      })
      .catch(error => {
        console.error('Error fetching clubs:', error.message);
        // You can also set an error state here if you want to display it in your UI
      });
  };

  return (
    <div>
      <div className="main-container">
        <div className="sidebar">
          <nav className="nav-container">
            <ul className="nav-links">
              <li>
                <Link to="/mainpage" className="login-btn" title="Home">
                  <i className="fa-solid fa-house"></i>
                </Link>
              </li>
              <li>
                <Link to="/login" className="login-btn" title="Login">
                  <i className="fa-solid fa-right-to-bracket"></i>
                </Link>
              </li>
              <li>
                <Link to="logout" className="login-btn" title="Logout">
                  <i className="fa-solid fa-right-to-bracket"></i>
                </Link>
              </li>
            </ul>
          </nav>
        </div>
        <div className="main-content">
          <div className="nav-top">
            <div className="logo">
              <img src="./logo.png" alt="logo" />
            </div>
          </div>
          <div className="clubs-container">
            {clubs.map(club => (
              <Clubcard key={club.id} club={club} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default MainPage;
