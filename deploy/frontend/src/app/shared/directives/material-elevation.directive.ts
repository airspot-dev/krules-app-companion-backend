import {
  Directive,
  ElementRef,
  HostListener,
  Input,
  Renderer2,
  OnChanges,
  SimpleChanges,
} from '@angular/core';

@Directive({
  selector: '[appMaterialElevation]',
})
export class MaterialElevationDirective implements OnChanges {
  @Input()
  defaultElevation = 2;

  @Input()
  raisedElevation = 8;

  constructor(private element: ElementRef, private renderer: Renderer2) {
    this.setElevation(this.defaultElevation);
  }

  ngOnChanges(_changes: SimpleChanges) {
    this.setElevation(this.defaultElevation);
  }

  @HostListener('mouseenter')
  onMouseEnter() {
    console.log('mouseenter', this.raisedElevation);
    this.setElevation(this.raisedElevation);
  }

  @HostListener('mouseleave')
  onMouseLeave() {
    console.log('mouseleave', this.defaultElevation);
    this.setElevation(this.defaultElevation);
  }

  setElevation(amount: number) {
    const elevationPrefix = 'mat-elevation-z';
    // remove all elevation classes
    const classesToRemove = Array.from(
      (<HTMLElement>this.element.nativeElement).classList
    ).filter((c) => c.startsWith(elevationPrefix));
    classesToRemove.forEach((c) => {
      this.renderer.removeClass(this.element.nativeElement, c);
    });

    // add the given elevation class
    const newClass = `${elevationPrefix}${amount}`;
    this.renderer.addClass(this.element.nativeElement, newClass);
  }
}
