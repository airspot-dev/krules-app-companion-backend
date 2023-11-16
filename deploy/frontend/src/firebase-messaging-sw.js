importScripts(
  "https://www.gstatic.com/firebasejs/9.18.0/firebase-app-compat.js"
);
importScripts(
  "https://www.gstatic.com/firebasejs/9.18.0/firebase-messaging-compat.js"
);
firebase.initializeApp({
  projectId: "airspot-krules-companion-dev",
  appId: "1:407615269082:web:8aa4b9fa489331f07d9de3",
  storageBucket: "airspot-krules-companion-dev.appspot.com",
  apiKey: "AIzaSyC2yQn0Fdm_Qh9Jm1dxjCpClTHyBEEKtlQ",
  authDomain: "airspot-krules-companion-dev.firebaseapp.com",
  messagingSenderId: "407615269082",
  measurementId: "G-FDXC6NFRQT",
});
const messaging = firebase.messaging();
