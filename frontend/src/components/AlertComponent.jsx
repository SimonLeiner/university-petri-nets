import { Alert, Slide } from '@mui/material';
import { useAlert } from '../providers/AlertProvider';

export const AlertComponent = () => {
  const { severity, message, showAlert } = useAlert();

  //renders alert if showAlert is true
  return (
    <Slide direction="up" in={showAlert} mountOnEnter unmountOnExit>
      <div className="fixed bottom-2 flex w-full justify-around z-50">
        <Alert severity={severity} className="w-fit">
          {message}
        </Alert>
      </div>
    </Slide>
  );
};

export default AlertComponent;