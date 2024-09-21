import PropTypes from 'prop-types';
import { createContext, useContext, useState } from 'react';

const AlertContext = createContext();

const AlertTime = 5000;

export const AlertProvider = ({ children }) => {
  const [severity, setSeverity] = useState();
  const [message, setMessage] = useState();
  const [showAlert, setShowAlert] = useState();

  const setAlert = (severity, message) => {
    if (message && severity) {
      setMessage(message);
      setSeverity(severity);
      setShowAlert(true);

      //set the showAlert to false to trigger closing animation in AlertComponent
      setTimeout(() => {
        setShowAlert(false);
        }, AlertTime);
    } else {
      console.error('Cant show Alert: Message or Severity of Alert undefined');
    }
  };

  return (
    <AlertContext.Provider value={{ severity, message, setAlert, showAlert }}>
      {children}
    </AlertContext.Provider>
  );
};

export const useAlert = () => {
  return useContext(AlertContext);
};

AlertProvider.propTypes = {
  children: PropTypes.node.isRequired,
};