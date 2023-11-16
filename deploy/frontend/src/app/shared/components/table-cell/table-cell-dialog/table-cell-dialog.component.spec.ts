import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TableCellDialogComponent } from './table-cell-dialog.component';

describe('TableCellDialogComponent', () => {
  let component: TableCellDialogComponent;
  let fixture: ComponentFixture<TableCellDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TableCellDialogComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TableCellDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
