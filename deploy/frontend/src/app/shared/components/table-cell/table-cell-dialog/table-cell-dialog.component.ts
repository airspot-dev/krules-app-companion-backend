import { AfterViewInit, Component, Inject, ViewChild } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { NgxMonacoEditorConfig } from 'ngx-monaco-editor-v2';

export interface DialogData {
  text: string;
}
interface EditorOptions {
  theme: string;
  language?: string;
  readOnly?: boolean;
  automaticLayout?: boolean;
  folding?: boolean;
}
@Component({
  selector: 'app-table-cell-dialog',
  templateUrl: './table-cell-dialog.component.html',
  styleUrls: ['./table-cell-dialog.component.scss'],
})
export class TableCellDialogComponent implements AfterViewInit {
  languages: string[] = ['json', 'plaintext', 'xml', 'yaml'];
  editor: any;
  language: string = 'plaintext';
  theme = 'vs-dark';
  original: string = '';
  editorOptions: EditorOptions;
  // text: string = 'function x() {\nconsole.log("Hello world!");\n}';
  constructor(
    public dialogRef: MatDialogRef<TableCellDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: DialogData
  ) {
    this.original = `${data.text}`;
    this.language = this._isJson(this.original) ? 'json' : 'plaintext';
    this.editorOptions = {
      theme: this.theme,
      language: this.language,
      readOnly: true,
      folding: true,
    };
  }

  _isJson(str: string) {
    try {
      JSON.parse(str);
    } catch (e) {
      return false;
    }
    return true;
  }

  ngAfterViewInit(): void {
    // console.log(thias.editor.getLanguages());
  }

  canRevert() {
    return this.original != this.data.text;
  }

  revert() {
    this.data.text = this.original;
  }
  format() {
    this.editorOptions = {
      theme: this.theme,
      language: this.language,
      readOnly: false,
    };
    setTimeout(() => {
      this.editor.getAction('editor.action.formatDocument').run();
    }, 50);
    setTimeout(() => {
      this.editorOptions = {
        theme: this.theme,
        language: this.language,
        readOnly: true,
      };
    }, 200);
  }

  onLanguageChange(evt: any) {
    this.editorOptions = {
      theme: this.theme,
      language: evt,
      readOnly: true,
    };
  }

  onEditorInit(editor: any) {
    this.editor = editor;
  }
}
