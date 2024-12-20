import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChannelCreateComponent } from './channel-create.component';

describe('ChannelCreateComponent', () => {
  let component: ChannelCreateComponent;
  let fixture: ComponentFixture<ChannelCreateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ChannelCreateComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChannelCreateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
