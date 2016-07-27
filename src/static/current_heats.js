var get_heat_status = function(stage) {
  return function() {
    $.ajax({
      type: "get",
      url: "/admin/current_heat/" + stage.substring(0, 1),
    }).done(function(data) {
      data = $.parseJSON(data);
      if (data.current_heat) {
        $("#" + stage + " > .icon").html("<img src='/static/img/e_" + data.current_heat.round.event.id + ".png'></img>");
        $("#" + stage + " > .eventname").html(data.current_heat.round.event.name + " Heat " + data.current_heat.number);
      } else {
        $("#" + stage + " > .icon").html("");
        $("#" + stage + " > .eventname").html("");
      }
      if (data.next_heat) {
        $("#" + stage + " > .nextup").html(data.next_heat.heat.round.event.name + " Heat " + data.next_heat.heat.number + " (" + data.next_heat.estimate + ")");
      } else {
        $("#" + stage + " > .nextup").html("");
      }
    });
  };
}

setInterval(get_heat_status('r'), 1000);
setInterval(get_heat_status('b'), 1000);
setInterval(get_heat_status('g'), 1000);
setInterval(get_heat_status('o'), 1000);
setInterval(get_heat_status('y'), 1000);
