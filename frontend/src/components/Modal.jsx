// src/components/Modal.js
import React, { useState } from 'react';
import {FaTimes} from "react-icons/fa"


const Modal = ({ isOpen, onClose, children }) => {

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 flex items-center justify-center">
          <div className="fixed inset-0 bg-black opacity-50"></div>
          <div className=" relative bg-white p-8 rounded shadow-lg z-10">
          <FaTimes onClick={onClose} className="absolute top-10 right-10"/>

            {children}
            {/* <button
              onClick={onClose}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
            >
              Close
            </button> */}
          </div>
        </div>
      )}
    </>
  );
};

export default Modal;
