import React, { useState, useEffect } from 'react';
import apiClient from '../utils/api';
import './InventoryDisplay.css';

const InventoryDisplay = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredInventory, setFilteredInventory] = useState([]);

  const fetchInventory = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/inventory');
      setInventory(response.data);
      setFilteredInventory(response.data);
    } catch (error) {
      console.error('Error fetching inventory:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (isModalOpen) {
      fetchInventory();
    }
  }, [isModalOpen]);

  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredInventory(inventory);
    } else {
      const filtered = inventory.filter(car => {
        const searchLower = searchTerm.toLowerCase();
        return (
          car.make.toLowerCase().includes(searchLower) ||
          car.model.toLowerCase().includes(searchLower) ||
          car.year.toString().includes(searchLower) ||
          car.stock_number.toLowerCase().includes(searchLower) ||
          car.vin.toLowerCase().includes(searchLower) ||
          (car.color && car.color.toLowerCase().includes(searchLower))
        );
      });
      setFilteredInventory(filtered);
    }
  }, [searchTerm, inventory]);

  return (
    <>
      <button 
        className="inventory-button"
        onClick={() => setIsModalOpen(true)}
      >
        View Live Inventory
      </button>

      {isModalOpen && (
        <div className="inventory-modal-overlay">
          <div className="inventory-modal">
            <div className="inventory-modal-header">
              <h2>Current Inventory</h2>
              <button 
                className="close-button"
                onClick={() => setIsModalOpen(false)}
              >
                ×
              </button>
            </div>
            
            <div className="inventory-search">
              <input
                type="text"
                placeholder="Search by make, model, year, stock #, VIN, or color..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
            
            <div className="inventory-modal-content">
              {loading ? (
                <div className="loading">Loading inventory...</div>
              ) : (
                <div className="inventory-list">
                  <div className="inventory-list-header">
                    <div className="header-cell">Year</div>
                    <div className="header-cell">Make</div>
                    <div className="header-cell">Model</div>
                    <div className="header-cell">Stock #</div>
                    <div className="header-cell">Price</div>
                    <div className="header-cell">Mileage</div>
                    <div className="header-cell">Color</div>
                  </div>
                  {filteredInventory.map((car) => (
                    <div key={car.id} className="inventory-item">
                      <div className="item-cell">{car.year}</div>
                      <div className="item-cell">{car.make}</div>
                      <div className="item-cell">{car.model}</div>
                      <div className="item-cell">{car.stock_number}</div>
                      <div className="item-cell">${car.price.toLocaleString()}</div>
                      <div className="item-cell">{car.mileage ? car.mileage.toLocaleString() : 'N/A'}</div>
                      <div className="item-cell">{car.color || 'N/A'}</div>
                    </div>
                  ))}
                  {filteredInventory.length === 0 && (
                    <div className="no-results">No matching vehicles found</div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default InventoryDisplay; 