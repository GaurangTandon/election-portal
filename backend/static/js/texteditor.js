tinymce.init({
  selector: 'textarea',
  plugins: 'table | wordcount | lists',
  menubar: '',
  toolbar: 'undo redo | formatselect | fontselect | bold italic underline strikethrough forecolor backcolor | alignleft aligncenter alignright alignjustify | numlist bullist | outdent indent',
  height: 900,
  toolbar_mode: 'floating',
  setup(editor) {
    editor.on('init', function () {
      this.setContent(`HI there!!!!${editor.id}`); // function to get manifesto data from db goes here
    });
  },
});

function postManifesto() { // function to post updated manifesto in db
  const content = tinyMCE.activeEditor.getContent();
  // console.log(content);

  return false;
}
