# Session Data Encryption

When you use a website or web application, the website needs to store certain information about your session, such as your user ID, preferences, or other data specific to your interaction with the site. However, it is important to protect this information from being accessed or tampered with by unauthorized individuals.

The session data encryption code provided in this repository helps ensure the security of your session data. It achieves this through the following steps:

1. **Unique Key Generation**: To start, a unique key is generated for each session. This key is created by combining various session variables, such as your browser type, cookie settings, local storage data, and more. By combining these variables, a unique key is created that identifies your session.

2. **Encryption**: When your session data needs to be stored, it is encrypted using the Advanced Encryption Standard (AES) algorithm. AES is a widely used encryption algorithm known for its security and effectiveness. To encrypt the data, a secret key derived from the unique session key is used. This ensures that only someone with the correct key can decrypt and access the data.

3. **Storage**: The encrypted session data is then stored in the local storage of your web browser. Local storage is a built-in feature of web browsers that allows websites to store data on your computer. By encrypting the session data before storing it, the information remains protected even if someone gains unauthorized access to the local storage.

4. **Decryption**: When you revisit the website or need to access your session data, the encrypted data is retrieved from the local storage. To make sense of this data, it needs to be decrypted. This is done by using the same secret key that was used for encryption. Only with the correct key can the data be successfully decrypted and returned to its original form.

5. **Clearing Data**: At times, it may be necessary to clear the session data stored in the local storage. This could happen when you log out of a website or when your session expires. The session data encryption code provides a function to remove the stored data from the local storage, ensuring that no sensitive information remains accessible after your session ends.

By employing these encryption techniques, the session data encryption code helps protect your sensitive information while it is stored in your web browser's local storage. This adds an extra layer of security to your online interactions and safeguards your personal data from unauthorized access.

---

I hope this explanation helps you understand how the session data encryption works without the need for technical knowledge. If you have any further questions, feel free to ask!

# Session Data Encryption

This repository contains a set of functions for encrypting and decrypting session data using the AES encryption algorithm. It provides a way to store and retrieve session data securely in the local storage of a web browser.

## Table of Contents

- [Session Data Encryption](#session-data-encryption)
- [Session Data Encryption](#session-data-encryption-1)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Usage](#usage)
  - [How Session and Encryption Work](#how-session-and-encryption-work)
    - [Session Variables](#session-variables)
    - [Generating a Unique Key](#generating-a-unique-key)
    - [Encrypting and Decrypting Data](#encrypting-and-decrypting-data)
    - [Storing and Retrieving Session Data](#storing-and-retrieving-session-data)
    - [Clearing Session Data](#clearing-session-data)
  - [Functions](#functions)
  - [Contributing](#contributing)
  - [License](#license)

## Introduction

In web applications, session data often needs to be stored and accessed across multiple pages or sessions. However, it is crucial to protect sensitive information stored in session data from unauthorized access. This repository provides a solution for securely encrypting and decrypting session data using AES encryption.

The code in this repository includes the following features:

- Creation of a unique key for each session based on various session variables.
- Encryption and decryption of session data using AES encryption.
- Storage of encrypted session data in the local storage of the web browser.
- Retrieval of encrypted session data from the local storage and its decryption for use in the application.
- Removal of session data from the local storage.

## Usage

To use the session data encryption functions in your web application, follow these steps:

1. Install the required dependencies by running the following command:

   ```
   npm install crypto-js
   ```

2. Import the necessary functions into your code:

   ```javascript
   import { createKeyCode, storeSessionData, retrieveSessionData, clearSessionData } from 'session-data-encryption';
   ```

3. Generate a unique key for each session by calling the `createKeyCode` function and passing the session variables as an object:

   ```javascript
   const sessionVariables = {
     userAgent: navigator.userAgent,
     cookiesEnabled: navigator.cookieEnabled,
     localStorage: window.localStorage.getItem('myData'),
     sessionStorage: window.sessionStorage.getItem('myData'),
     notifications: getNotifications(),
     dom: getDOM(),
     webWorkers: supportsWebWorkers(),
     geolocation: getCurrentLocation(),
   };

   const keyCode = createKeyCode(sessionVariables);
   ```

4. Store session data securely in the local storage by calling the `storeSessionData` function and passing the key, data, and the generated keyCode:

   ```javascript
   const sessionData = {
     userId: 12345,
     username: 'john_doe',
     role: 'admin',
   };

   storeSessionData('mySession', sessionData, keyCode);
   ```

5. Retrieve session data from the local storage by calling the `retrieveSessionData` function and passing the key and the keyCode:

   ```javascript
   const retrievedData = retrieveSessionData('mySession', keyCode);
   console.log(retrievedData);
   ```

6. Clear session data from the local storage by calling the `clearSessionData` function and passing the key:

   ```javascript
   clearSessionData('mySession');
   ```

## How Session and Encryption Work

### Session Variables

Session variables are essential components used to create a unique key for each session. These variables represent different aspects of the user's session, such as the user agent, cookie status, local storage data, session storage data, notifications, DOM information, support for web workers, and geolocation. By combining these variables, a session-specific key is generated.

### Generating a Unique Key

The `createKeyCode` function takes an object `variables` of type `SessionVariables` as input. It concatenates all the values of the `variables` object into a single string. This concatenated string represents a unique combination of the session variables. To ensure security, a SHA-256 hash of the concatenated string is created using the `crypto-js` library. The resulting hash is returned as a hexadecimal string, serving as the unique key for the session.

### Encrypting and Decrypting Data

The `encryptData` function accepts a `data` string and a `keyCode` string as input. It encrypts the `data` using the AES encryption algorithm provided by the `crypto-js` library. AES (Advanced Encryption Standard) is a widely used symmetric encryption algorithm known for its security and efficiency. The `keyCode` serves as the encryption key for the AES algorithm. The encrypted data is returned as a string.

The `decryptData` function takes a `ciphertext` string and a `keyCode` string as input. It decrypts the `ciphertext` using the AES decryption algorithm provided by the `crypto-js` library. The `keyCode` is used as the decryption key. The decrypted data is returned as a UTF-8 encoded string.

### Storing and Retrieving Session Data

The `storeSessionData` function allows you to securely store session data in the local storage of the web browser. It accepts a `key` string, `data` of any type, and a `keyCode` string as input. The `data` object is first converted to a JSON string. Then, the JSON string is encrypted using the `encryptData` function with the provided `keyCode`. The resulting encrypted data is stored in the local storage using the `key` as the identifier.

To retrieve the stored session data, the `retrieveSessionData` function is used. It takes a `key` string and a `keyCode` string as input. The function retrieves the encrypted data associated with the `key` from the local storage. If no data is found, it returns `null`. If data is found, it decrypts the data using the `decryptData` function with the provided `keyCode`, parses the decrypted JSON string, and returns the resulting object.

### Clearing Session Data

The `clearSessionData` function allows you to remove session data from the local storage. It takes a `key` string as input and removes the data associated with the `key` from the local storage.

## Functions

The following functions are available in this repository:

- `createKeyCode(variables: SessionVariables): string`: Creates a unique key for each session based on the provided session variables.

- `encryptData(data: string, keyCode: string): string`: Encrypts the provided data using AES encryption with the given keyCode.

- `decryptData(ciphertext: string, keyCode: string): string`: Decrypts the provided ciphertext using AES decryption with the given keyCode.

- `storeSessionData(key: string, data: any, keyCode: string)`: Stores the provided data securely in the local storage using encryption.

- `retrieveSessionData(key: string, keyCode: string): any`: Retrieves the encrypted data associated with the provided key from the local storage, decrypts it, and returns the original data.

- `clearSessionData(key: string)`: Removes the data associated with the provided key from the local storage.

## Contributing

Contributions to this project are welcome! If you find any issues or would like to suggest enhancements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use and modify the code according to your needs.

---

Feel free to customize and expand upon this README template to suit your specific requirements. Include any additional information or instructions that may be relevant to your application's session data encryption process.