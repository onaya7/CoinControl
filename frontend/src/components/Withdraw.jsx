import React, { useState, useEffect } from "react";
import { useModal } from "../context/ModalContext";
import axios from "axios";

import Modal from "../components/Modal";

const Withdraw = ({ closeModal }) => {
  const { isModalOpen, openModal } = useModal();
  const [budgets, setBudgets] = useState([]);
  const [selectedBudget, setSelectedBudget] = useState("");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [accountNumber, setAccountNumber] = useState("");
  const [bankName, setBankName] = useState("");

  useEffect(() => {
    fetchBudgets();
  }, []);

  const fetchBudgets = async () => {
    try {
      const token = localStorage.getItem("accessToken");

      const response = await axios.get(`${import.meta.env.VITE_APP_URL}/budgets`,{
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const budgetData = response.data.data.data;
      setBudgets(budgetData);
    } catch (error) {
      console.error("Error fetching budgets:", error);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const withdrawalData = {
      name: selectedBudget,
      amount,
      description,
      account_number: accountNumber,
      bank_name: bankName,
    };

    try {
      await axios.post(
        `${import.meta.env.VITE_APP_URL}/expenses`,
        withdrawalData,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
          },
        }
      );

      alert("Withdrawal request submitted successfully.");

      setSelectedBudget("");
      setAmount("");
      setDescription("");
      setAccountNumber("");
      setBankName("");
    } catch (error) {
      console.error("Error submitting withdrawal request:", error);
      alert("Failed to submit withdrawal request.");
    }
  };

  return (
    <Modal isOpen={isModalOpen} onClose={closeModal}>
      <div className="bg-white p-6 rounded-md shadow-md">
        <h2 className="text-xl font-semibold mb-4 text-[#EE6338]">
          Initiate Withdrawal
        </h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col">
          <label htmlFor="selectedBudget" className="font-semibold text-gray-700">Budget:</label>
          <select
            id="selectedBudget"
            value={selectedBudget}
            onChange={(event) => setSelectedBudget(event.target.value)}
            required
            className="w-full p-2 border border-gray-300 focus:outline-none"
          >
            <option value="">Select a budget</option>
            {budgets.map((budget) => (
              <option key={budget.id} value={budget.name}>
                {budget.name}
              </option>
            ))}
          </select>
          </div>

          <div className="flex flex-col">
            <label htmlFor="amount" className="font-semibold text-gray-700">
              Amount:
            </label>
            <input
              id="amount"
              type="number"
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              required
              className="w-full p-2 border border-gray-300 focus:outline-none"
            />
          </div>

          <div className="flex flex-col">
            <label
              htmlFor="description"
              className="font-semibold text-gray-700"
            >
              Description:
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              className="w-full p-2 border border-gray-300 focus:outline-none"
            />
          </div>

          <div className="flex flex-col">
            <label
              htmlFor="accountNumber"
              className="font-semibold text-gray-700"
            >
              Account Number:
            </label>
            <input
              id="accountNumber"
              type="text"
              value={accountNumber}
              onChange={(event) => setAccountNumber(event.target.value)}
              required
              className="w-full p-2 border border-gray-300 focus:outline-none"
            />
          </div>

          <div className="flex flex-col">
            <label htmlFor="bankName" className="font-semibold text-gray-700">
              Bank Name:
            </label>
            <input
              id="bankName"
              type="text"
              value={bankName}
              onChange={(event) => setBankName(event.target.value)}
              required
              className="w-full p-2 border border-gray-300 focus:outline-none"
            />
          </div>

          <button
            type="submit"
            className="bg-[#EE6338] text-white font-semibold p-2 rounded-md w-full"
          >
            Withdraw
          </button>
        </form>
      </div>
    </Modal>
  );
};

export default Withdraw;
