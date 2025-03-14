function openBalanceForm() {
    document.getElementById("balance-form").style.display="block";
    document.getElementById("currency").style.display="none";
    document.getElementById("amount").style.display="none";
    document.getElementById("goals").style.top="350px";
  }
  
  function closeBalanceForm() {
    document.getElementById("balance-form").style.display="none";
    document.getElementById("goals").style.top="270px";
  }

  function openGoalsForm() {
      document.getElementById("goals-form").style.display = "block";
      document.getElementById("goals-content").style.display = "none";
      document.getElementById("goals").style.marginBottom = "10px";
  }
  
  function closeGoalsForm() {
      document.getElementById("goals-form").style.display = "none";
      document.getElementById("goals-content").style.display = "block"; // Add this line
  }
  
  function openExpensesForm() {
      document.getElementById("expenses-form").style.display = "block";
      document.getElementById("expenses-content").style.display = "none";
      document.getElementById("expenses").style.paddingBottom = "10px";
  }
  
  function closeExpensesForm() {
      document.getElementById("expenses-form").style.display = "none";
      document.getElementById("expenses-content").style.display = "block"; // Add this line
  }