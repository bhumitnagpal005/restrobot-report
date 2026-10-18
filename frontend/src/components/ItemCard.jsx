import React from 'react';

export default function ItemCard({ item, showConstraintStatus = true }) {
  const restName = item.restaurant_name || "Restaurant";
  const name = item.item_name || "Menu Item";
  const price = item.price || 0;
  const isVeg = item.is_vegetarian;
  const isNonVeg = item.is_non_vegetarian;
  const spice = item.spice_level || "normal";
  const score = item.retrieval_score || item.final_score || 0;
  const isConstraintValid = item.is_valid_constraint !== false;
  const violations = item.constraint_violations || [];

  return (
    <div style={{
      background: '#1e293b',
      border: isConstraintValid ? '1px solid #334155' : '1px solid rgba(239, 68, 68, 0.5)',
      borderRadius: '8px',
      padding: '12px',
      marginBottom: '8px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
        <div>
          <span style={{ fontSize: '0.73rem', fontWeight: 600, color: '#ff6b35', textTransform: 'uppercase' }}>
            {restName}
          </span>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#f8fafc' }}>
            {name}
          </h4>
        </div>
        <div style={{ textAlign: 'right' }}>
          <span style={{ fontSize: '1rem', fontWeight: 700, color: '#10b981' }}>
            ₹{price.toFixed(0)}
          </span>
          {score > 0 && (
            <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
              Score: {score.toFixed(3)}
            </div>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '8px' }}>
        {isVeg && <span className="badge badge-veg">🌱 Vegetarian</span>}
        {isNonVeg && <span className="badge badge-nonveg">🍗 Non-Veg</span>}
        {spice && spice !== 'normal' && <span className="badge badge-spice">🌶️ {spice}</span>}
        {item.category && <span className="badge badge-constraint">{item.category}</span>}
      </div>

      {item.description && (
        <p style={{ fontSize: '0.8rem', color: '#94a3b8', lineHeight: '1.4' }}>
          {item.description}
        </p>
      )}

      {showConstraintStatus && !isConstraintValid && (
        <div style={{
          marginTop: '8px',
          padding: '6px 8px',
          background: 'rgba(239, 68, 68, 0.1)',
          borderRadius: '4px',
          fontSize: '0.73rem',
          color: '#f87171'
        }}>
          ⚠️ Constraint Failure: {violations.join(", ")}
        </div>
      )}
    </div>
  );
}
