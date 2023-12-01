import React, { useState } from "react";
import AddBudgetForm from "../components/AddBudgetForm";
import DashBoardBudget from "./DashBoardBudget";
const Budget = () => {
  const [budgets, setBudgets] = useState([]);
  const [isFormVisible, setFormVisibility] = useState(false);

  const handleBudgetAdded = (newBudget) => {
    // Update the budgets state with the new budget
    setBudgets([...budgets, newBudget]);
    //   setFormVisibility(false); // Hide the form after adding a budget
  };
  
  return (
    <div>
      {/* <button onClick={() => setFormVisibility(!isFormVisible)}>
        {isFormVisible ? "" : "Add New Budget"}
      </button> */}
      <DashBoardBudget budgets={budgets} />
      <AddBudgetForm onBudgetAdded={handleBudgetAdded} />
    {/* {isFormVisible && <AddBudgetForm onBudgetAdded={handleBudgetAdded} />} */}
    </div>
  );
};

export default Budget;
