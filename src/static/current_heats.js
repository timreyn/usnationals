var get_heat_status = function(stage) {
  return function() {
    $.ajax({
      type: "get",
      url: "/current_heat/" + stage.substring(0, 1),
    }).done(function(data) {
      if (data.current_heat) {
        $("#" + stage + " > .current > .icon").html("<img src='/static/img/e_" + data.current_heat.round.event.id + ".png'></img>");
        $("#" + stage + " > .current > .eventname").html(data.current_heat.number);
      } else {
        $("#" + stage + " > .current > .icon").html("");
        $("#" + stage + " > .current > .eventname").html("");
      }
      if (data.next_heat) {
        $("#" + stage + " > .nextevent > .icon").html("<img src='/static/img/e_" + data.next_heat.heat.round.event.id + ".png'></img>");
        $("#" + stage + " > .nextevent > .eventname").html(data.next_heat.heat.number + " (" + data.next_heat.estimate + ")");
      } else {
        $("#" + stage + " > .nextevent > .icon").html("");
        $("#" + stage + " > .nextevent > .eventname").html("");
      }
    });
  };
}

setInterval(get_heat_status('r'), 30000);
setInterval(get_heat_status('b'), 30000);
setInterval(get_heat_status('g'), 30000);
setInterval(get_heat_status('o'), 30000);
setInterval(get_heat_status('y'), 30000);

get_heat_status('r')();
get_heat_status('b')();
get_heat_status('g')();
get_heat_status('o')();
get_heat_status('y')();
