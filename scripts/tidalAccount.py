import tidalapi
import json
import pathlib
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TidalAccount():

    def __init__(self, credential_file: str = "tidal"):
        """ Initialise Tidal session, restore from saved credentials if possible """

        # Pointer to session
        self._session = tidalapi.Session()

        # Set location for storing credentials
        working_dir = pathlib.Path.cwd()
        if not credential_file.endswith('.json'):
            credential_file += '.json'
        self._credentials = working_dir / credential_file

        # Try to restore session, or create a new one if the restoration fails
        if not self._restore_session():
            self._new_session()
        
        # Sanity check on login
        if not self._session.check_login():
            logging.error("Could not log in to Tidal. Exiting...")
            exit(1)

    def _restore_session(self) -> bool:
        """ Restore session from the credentials file if it exists """

        logging.debug("Attempting to restore Tidal session from saved credentials...")

        if self._credentials.exists():

            logging.debug(f"Found credentials file at {self._credentials}")

            with open(self._credentials, 'r') as f:
                creds = json.load(f)

            token_type = creds.get('token_type')
            access_token = creds.get('access_token')
            refresh_token = creds.get('refresh_token')
            expiry_time = creds.get('expiry_time')

            if expiry_time:
                expiry_time = datetime.fromisoformat(expiry_time)
                self._session.load_oauth_session(
                    token_type=token_type,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expiry_time=expiry_time
                )
            else:
                self._session.load_oauth_session(
                    token_type=token_type,
                    access_token=access_token,
                    refresh_token=refresh_token
                )

            if self._session.check_login():
                logging.info("Restored Tidal session from saved credentials")
                return True
        
        else:
            logging.debug("Credentials file not found")

        return False
    
    def _save_session(self) -> None:
        """ Save the current session to the credentials .json file """

        logging.info(f"Saving OAuth credentials to {self._credentials}...")
        
        try:
            creds = {
                'token_type': self._session.token_type,
                'access_token': self._session.access_token,
                'refresh_token': self._session.refresh_token,
                'expiry_time': self._session.expiry_time.isoformat() if self._session.expiry_time else None
            }

            with open(self._credentials, 'w') as f:
                json.dump(creds, f)
                logging.debug(f"Written credentials to {f.name}")
        
        except Exception as e:
            logging.error(f"Error saving credentials: {e}")
    
    def _new_session(self) -> None:
        """ Create a new Tidal session via OAuth, store credentials for future use """

        logging.info("Creating new Tidal session via OAuth...")

        self._session.login_oauth_simple()

        if self._session.check_login():
            logging.info("Sucessfully created new Tidal session")
            self._save_session()
        
        else:
            logging.error("Failed to create new Tidal session. Exiting...")
            exit(1)

if __name__ == "__main__":

    tidal = TidalAccount()