fetch("/api/v1/allbusstopinfo")
  .then((response) => response.json())
  .then((data) => {
    miniSearch.addAll(data);
  });
var miniSearch = new MiniSearch({
  fields: ["bus_stop_code", "description", "road_name"], // fields to index for full-text search
  storeFields: ["bus_stop_code", "description", "road_name"], // fields to return with search results
});
function showCode(inputName) {
  let target = document.getElementById(`${inputName}_stop_code`);
  let results = miniSearch.search(target.value, {
    fields: ["bus_stop_code"],
  });
  var text;
  if (
    results[0] === undefined ||
    results.length > 1 ||
    target.value.length < 5
  ) {
    text =
      '<span style="color:red; font-family: Georgia, serif">Invalid Bus Stop Code</span>';
  } else {
    let result = results[0];
    text = `${result.bus_stop_code} ${result["description"]}, ${result.road_name}`;
  }

  target.nextElementSibling.innerHTML = text;
  hideList(inputName);
}

function inputChange(inputName) {
  let elm = document.getElementById(`${inputName}_stop_code`);
  let searchResults = miniSearch.search(elm.value, {
    fuzzy: 0.2,
    prefix: true,
  });

  var list = document.getElementById(`${inputName}-autosuggestion-list`);
  list.innerHTML = ""; // clear the results
  for (let result of searchResults.slice(0, 5)) {
    let as_item = document.createElement("li");
    as_item.classList.add("autosuggestion-item");
    as_item.innerHTML = `${result.bus_stop_code} ${result["description"]}, ${result.road_name}`;
    as_item.onmousedown = (e) => {
      elm.value = `${result.bus_stop_code}`;
    };
    list.appendChild(as_item);
  }
}
function displayList(inputName) {
  var list = document.getElementById(`${inputName}-autosuggestion-list`);
  list.style.display = "block";
}
function hideList(inputName) {
  var list = document.getElementById(`${inputName}-autosuggestion-list`);
  list.style.display = "none";
}
