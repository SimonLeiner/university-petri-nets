import React from 'react';

const ConformanceComponent = ({ conformance }) => {
  return (
    <div className="conformance-area">
      <h2>Conformance Checking</h2>
      <table>
        <thead>
          <tr>
            <th>Metric</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(conformance).map(([key, value]) => (
            <tr key={key}>
              <td>{key}</td>
              <td>{value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ConformanceComponent;
