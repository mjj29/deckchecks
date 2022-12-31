import { Component, OnInit, Inject, Input } from '@angular/core';
import { IPairings } from "../../apis/pairings/pairings.api";
import { MatTableDataSource, MatSort } from '@angular/material';

@Component({
	selector: 'app-pairings',
	templateUrl: './pairings.component.html',
	styleUrls: ['./pairings.component.css']
})
export class PairingsComponent implements OnInit {

	@Input('round') public round: number;
	@Input('event') public event: number;
	@Input("pairings") public pairings: IPairings;
	public indexes=[1, 2];

	ngOnInit(): void { }

}

