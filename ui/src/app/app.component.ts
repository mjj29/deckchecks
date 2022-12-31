import { Component, OnInit, Inject, ViewChild } from '@angular/core';
import { IPairings } from "./apis/pairings/pairings.api";
import { PairingsService } from "./apis/pairings/pairings.service";
import { Observable } from 'rxjs';
import { MatExpansionPanel } from '@angular/material/expansion';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'deckchecks';
  round = 1;
  event = 1;
	public pairings$: Observable<IPairings>;
	@ViewChild('tablePanel', {static: true, read: MatExpansionPanel}) tablePanel: MatExpansionPanel;
	@ViewChild('pairingsPanel', {static: true, read: MatExpansionPanel}) pairingsPanel: MatExpansionPanel;
	@ViewChild('checksPanel', {static: true, read: MatExpansionPanel}) checksPanel: MatExpansionPanel;
	ngOnInit(): void {
		this.pairings$=this._pairingsService.getPairings(this.round, this.event);
		this.pairings$.subscribe(data => console.log(data));
	}
	constructor(private _pairingsService: PairingsService)
	{
	}

	togglePanel(id: MatExpansionPanel): void {
		id.toggle();
		if (id != this.tablePanel) { this.tablePanel.close(); }
		if (id != this.checksPanel) { this.checksPanel.close(); }
		if (id != this.pairingsPanel) { this.pairingsPanel.close(); }
	}


}
