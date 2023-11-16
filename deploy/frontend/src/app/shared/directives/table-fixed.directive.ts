import {
  Directive,
  ElementRef,
  Input,
  OnChanges,
  OnInit,
  Renderer2,
  SimpleChanges,
} from '@angular/core';

@Directive({
  selector: '[appTableFixed]',
})
export class TableFixedDirective implements OnChanges, OnInit {
  private _collapsed = false;

  @Input()
  set isCollapsed(value: boolean) {
    this._collapsed = !!value;
    this.calcTableDimensions();
  }

  @Input()
  set isLoaded(value: boolean) {
    this.calcTableDimensions();
    if (value)
      setTimeout(() => {
        this.calcTableDimensions();
      }, 250);
  }

  constructor(private element: ElementRef, private renderer: Renderer2) {
    window.addEventListener(
      'resize',
      () => {
        this.calcTableDimensions();
      },
      true
    );
  }

  ngOnInit(): void {
    this.calcTableDimensions();
  }

  ngOnChanges(_changes: SimpleChanges) {
    this.calcTableDimensions();
  }

  private _getStyle(oElm: any, strCssRule: any) {
    var strValue = '';
    if (document.defaultView && document.defaultView.getComputedStyle) {
      strValue = document.defaultView
        .getComputedStyle(oElm, '')
        .getPropertyValue(strCssRule);
    } else if (oElm.currentStyle) {
      strCssRule = strCssRule.replace(
        /\-(\w)/g,
        (strMatch: string, p1: string) => {
          return p1.toUpperCase();
        }
      );
      strValue = oElm.currentStyle[strCssRule];
    }
    return strValue;
  }

  calcTableDimensions() {
    const w = this.calcTableWidth();
    //const h = this.calcTableHeight();
    const styles = [
      { property: 'width', value: w },
      //{ property: 'height', value: h },
      { property: 'overflow', value: 'auto' },
    ];
    styles.forEach((s) =>
      this.renderer.setStyle(this.element.nativeElement, s.property, s.value)
    );
  }

  calcTableWidth() {
    const gapNotCollapsed = '1.5rem';
    const gapCollapsed = '55px';
    const margin = '2rem';
    const sidebar = document.getElementById('kr-sidebar');
    const krSideBarW = sidebar ? '300px' : 0;
    // const viewport = window.innerWidth;

    const krTable = document.getElementById('kr-table');
    if (!krTable) return {}; //return { width: '1515px', overflow: 'auto' };
    const paddingLeft = this._getStyle(krTable, 'padding-left').replace(
      'px',
      ''
    );
    const padding = `${parseInt(paddingLeft) * 2}px`;
    return `calc(${document.documentElement.clientWidth}px - ${margin} - ${
      this._collapsed ? gapCollapsed : gapNotCollapsed
    } - ${this._collapsed ? '0px' : krSideBarW} - ${padding})`;
  }
  calcTableHeight() {
    const sidebar = document.getElementById('kr-sidebar');
    const header = document.getElementById('group-table-header');
    const krTable = document.getElementById('kr-table');
    if (!header && !krTable) return 0;
    const paginator = document.getElementsByClassName('mat-mdc-paginator')[0];
    const filterKV = document.getElementsByTagName('app-key-value-filter')[0];
    const filterCD = document.getElementsByTagName('app-column-date-filter')[0];
    const paginatorMT = this._getStyle(paginator, 'margin-top');

    const referenceH = (sidebar || krTable)!.offsetHeight + 'px';
    const headerH = header ? header.offsetHeight + 'px' : 0;
    const filterH =
      filterKV || filterCD
        ? ((filterKV || filterCD) as HTMLElement).offsetHeight + 'px'
        : 0;
    const paginatorH = paginator!.clientHeight + 'px';

    if (!krTable) return {}; //return { width: '1515px', overflow: 'auto' };
    const paddingLeft = this._getStyle(krTable, 'padding-left').replace(
      'px',
      ''
    );
    const padding = `${parseInt(paddingLeft) * 2}px`;
    return `calc( ${referenceH} - 0.5rem - ${headerH} - ${filterH} - ${paginatorH} - ${paginatorMT} -  ${padding})`;
  }
}
