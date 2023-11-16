import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {
  opened: boolean = true;
  events: string[] = [];
  constructor() {}

  ngOnInit(): void {}
}
