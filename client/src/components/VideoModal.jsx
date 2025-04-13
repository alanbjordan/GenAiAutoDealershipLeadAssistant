import React from 'react';
import './VideoModal.css';

const VideoModal = ({ isOpen, onClose, videos }) => {
  if (!isOpen) return null;

  console.log('VideoModal rendering with videos:', videos);

  return (
    <div className="video-modal-overlay">
      <div className="video-modal-content">
        <button className="video-modal-close" onClick={onClose}>×</button>
        <h2>Car Review Videos</h2>
        <div className="video-list">
          {videos && videos.length > 0 ? (
            videos.map((video, index) => (
              <div key={index} className="video-item">
                <h3>{video.title}</h3>
                <div className="video-container">
                  <iframe
                    src={video.url}
                    title={video.title}
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  ></iframe>
                </div>
                <p className="video-description">{video.description}</p>
              </div>
            ))
          ) : (
            <div className="no-videos-message">
              <p>No videos found. Please try a different search.</p>
              <p className="error-details">This could be due to:</p>
              <ul>
                <li>No videos available for this specific car</li>
                <li>YouTube API key not configured</li>
                <li>API rate limiting</li>
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoModal; 