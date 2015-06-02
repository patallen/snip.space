window.onload = function () {
  
    var editableCodeMirror = CodeMirror.fromTextArea(document.getElementById('snippet_editable'), {
        mode: "javascript",
        theme: "default",
        lineNumbers: true
    });

    var readOnlyCodeMirror = CodeMirror.fromTextArea(document.getElementById('snippet_readonly'), {
        mode: "javascript",
        theme: "default",
        lineNumbers: true,
        readOnly: true
    });  
};