fetch("http://127.0.0.1:5000/api/v1/allbusstopinfo")
  .then((response) => response.json())
  .then((data) => {
    miniSearch.addAll(data);
  });
let miniSearch = new MiniSearch({
  fields: ["bus_stop_code", "description", "road_name"], // fields to index for full-text search
  storeFields: ["bus_stop_code", "description", "road_name"], // fields to return with search results
  tokenise: (string, _fieldname) => string,
});
function showOption(tag) {
  document.getElementById(tag).classList.toggle("show");
}
function showCode(target) {
  target = document.getElementById(target);
  results = miniSearch.search(target.value, {
    fields: ["bus_stop_code"],
  });
  if (
    results[0] === undefined ||
    results.length > 1 ||
    target.value.length < 5
  ) {
    text =
      '<span style="color:red; font-family: Georgia, serif">Invalid Bus Stop Code</span>';
  } else {
    result = results[0];
    text = `${result.bus_stop_code} ${result["description"]}, ${result.road_name}`;
  }
  target.parentElement.lastElementChild.innerHTML = text;
}
