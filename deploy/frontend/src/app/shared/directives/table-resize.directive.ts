import {
  AfterViewInit,
  Directive,
  ElementRef,
  HostListener,
  Input,
  OnInit,
  Renderer2,
} from '@angular/core';

@Directive({
  selector: '[appTableResize]',
})
export class TableResizeDirective implements OnInit {
  @Input('appTableResize') resizable: boolean = false;
  @Input() index: number = -1;
  private startX: number = -1;
  private startWidth: number = -1;
  private column: HTMLElement;
  private table?: HTMLElement;
  private pressed: boolean = false;
  constructor(private renderer: Renderer2, private el: ElementRef) {
    this.column = this.el.nativeElement;
    console.log('appTableResize');
  }

  ngOnInit() {
    if (this.resizable) {
      const row = this.renderer.parentNode(this.column);
      const thead = this.renderer.parentNode(row);
      this.table = this.renderer.parentNode(thead);
      const resizer = this.renderer.createElement('span');
      this.renderer.addClass(resizer, 'resize-holder');
      this.renderer.appendChild(this.column, resizer);
      this.renderer.listen(resizer, 'mousedown', this.onMouseDown);
      this.renderer.listen('document', 'mouseup', this.onMouseUp);
      this.renderer.listen(this.table, 'mousemove', this.onMouseMove);
    }
  }

  onMouseDown = (event: MouseEvent) => {
    console.log('onMouseDown');
    this.pressed = true;
    this.startX = event.pageX;
    this.startWidth = this.column.offsetWidth;
  };

  onMouseMove = (event: MouseEvent) => {
    const offset = 35;
    if (this.pressed && event.buttons) {
      this.renderer.addClass(this.table, 'resizing');

      // Calculate width of column
      let width = this.startWidth + (event.pageX - this.startX - offset);
      if (!this.table) return;
      const tableCells = Array.from(
        this.table.querySelectorAll('.mat-row')
      ).map((row: any) => row.querySelectorAll('.mat-cell').item(this.index));

      // Set table header width
      this.renderer.setStyle(this.column, 'width', `${width}px`);
      console.log(width);
      // Set table cells width
      for (const cell of tableCells) {
        this.renderer.setStyle(cell, 'width', `${width}px`);
      }
    }
  };

  onMouseUp = (event: MouseEvent) => {
    console.log('onMouseUp');
    if (this.pressed) {
      this.pressed = false;
      this.renderer.removeClass(this.table, 'resizing');
    }
  };
}
