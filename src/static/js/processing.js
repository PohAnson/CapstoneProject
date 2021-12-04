count = 0;
fetch("/finding_path");
gettingApi = window.setInterval(function () {
  fetch("/api/v1/status")
    .then((response) => response.json())
    .then(function (data) {
      count += 1;
      if (!data.status_done) {
        data["main_status"] = data["main_status"] + ".".repeat(count % 4);
      } else {
        console.log("finish");
        window.clearInterval(gettingApi);
        console.log("cleared interval");
        window.location = "/results";
      }
      document.getElementById("main-status").innerText = data["main_status"];
      document.getElementById("sub-status").innerText = data["sub_status"];
    });
}, 500);
