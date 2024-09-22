import { Alert, Slide } from '@mui/material';
import { useAlert } from '../providers/AlertProvider';

export const AlertComponent = () => {
  const { severity, message, showAlert } = useAlert();

  // Renders alert if showAlert is true
  return (
    <Slide direction="up" in={showAlert} mountOnEnter unmountOnExit>
      <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50">
        <Alert severity={severity} className="w-fit">
          {message}
        </Alert>
      </div>
    </Slide>
  );
};

export default AlertComponent;
