function next(button, checkbox, triggerButton) {
  var buttonElement = button;
  buttonElement.remove();

  var checkboxElement = checkbox;
  checkboxElement.remove();

  var triggerButtonElement = triggerButton;
  triggerButtonElement.innerHTML = "Generate";
}

function generate() {}
