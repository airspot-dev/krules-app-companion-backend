import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TokenCreateComponent } from './token-create.component';

describe('TokenCreateComponent', () => {
  let component: TokenCreateComponent;
  let fixture: ComponentFixture<TokenCreateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TokenCreateComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TokenCreateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
