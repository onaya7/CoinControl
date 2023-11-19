import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useModal } from "../context/ModalContext";

import axios from "axios";
import Modal from "../components/Modal";

const AddIncome = ({closeModal}) => {
  const { isModalOpen, openModal  } = useModal();

  const [amount, setAmount] = useState("");
  const navigate = useNavigate()
 

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const token = localStorage.getItem("accessToken");
      const response = await axios.put(
        `${import.meta.env.VITE_APP_URL}/income`,
        {
          amount: parseFloat(amount), // Assuming amount is a number
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.status === 201 || response.data.status === "success") {
        // Clear form fields
        setAmount("");
        navigate('/dashboard/me');

        // Notify parent component about the added budget
      } else {
        throw new Error("Failed to add income");
      }
    } catch (error) {
      console.error("Error adding income:", error);
    }
  };

  return (
    <Modal isOpen={isModalOpen} onClose={closeModal}>
     <div className="bg-white p-6 rounded-md shadow-md">
      <h2 className="text-xl font-semibold mb-4 text-[#EE6338]">Top Up Income</h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col">
          <label htmlFor="amount" className="font-semibold text-gray-700">Amount:</label>
          <input
            id="amount"
            type="number"
            value={amount}
            onChange={(event) => setAmount(event.target.value)}
            required
            className="w-full p-2 border border-gray-300 focus:outline-none"
          />
        </div>

        <button type="submit" className="bg-[#EE6338] text-white font-semibold p-2 rounded-md w-full">Top Up</button>
      </form>
    </div>
    </Modal>
  );
};

export default AddIncome;
