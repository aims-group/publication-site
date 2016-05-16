data = Bind({
  // data
  name: '',
  list: []
}, {
  // bind mapping
  name: '#click-id',
  list: {
    dom: '#click-stats',
    transform: function (val) {
        return '<li>' + this.safe(val) + '</li>';
    },
  }
});