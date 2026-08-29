import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from erd import Diagram

COL = {0: 50, 1: 465, 2: 880, 3: 1295, 4: 1710}
ROW = {0: 110, 1: 450, 2: 820}

d = Diagram(cols=COL, rows=ROW, width=2160, height=1270)

d.add("mutations", 0, 0, "indigo", [
    ("id", "pk"), ("transformation_id", "fk", "indigo"), ("source_protein_id", "fk", "indigo"),
    ("pos",), ("pos_end",), ("source_aa",), ("target_aa",)])
d.add("transformations", 1, 0, "indigo", [
    ("id", "pk"), ("source_protein_id", "fk", "indigo"), ("target_protein_id", "fk", "indigo"),
    ("mutation_class",)])
d.add("proteins", 2, 0, "indigo", [("id", "pk"), ("sequence_sha256", "uq"), ("aa_sequence",)])
d.add("structure_protein_relatability", 3, 0, "red", [
    ("structure_id", "pk fk", "teal"), ("protein_id", "pk fk", "indigo")], accent=True)
d.add("structures", 4, 0, "teal", [
    ("id", "pk"), ("source",), ("source_id",), ("polymer_content_sha256",), ("file_ref",),
    ("derived_from_structure_id", "fk", "teal"), ("cache_key", "fk", "grey"),
    ("data_layer_id", "fk", "grey")])
d.add("protein_reference_frames", 1, 1, "indigo", [
    ("protein_id", "pk fk", "indigo"), ("reference_protein_id", "fk", "indigo"),
    ("protein_start",), ("protein_end",), ("reference_offset",)])
d.add("protein_docking_jobs", 2, 1, "red", [
    ("compute_job_id", "pk fk", "grey"), ("analysis_protein_id", "fk", "indigo"),
    ("hit_experiment_protein_id", "fk", "indigo"), ("hitset_id",)], accent=True)
d.add("structure_chain_anchors", 3, 1, "teal", [
    ("structure_id", "pk fk", "teal"), ("chain", "pk"),
    ("reference_protein_id", "fk", "indigo"), ("covered_positions",), ("mismatched_positions",)])
d.add("pockets", 4, 1, "amber", [
    ("id", "pk"), ("structure_id", "fk", "teal"), ("protein_id", "fk", "indigo"), ("source",),
    ("rank",), ("center_x  center_y  center_z",), ("residue_positions",),
    ("cache_key", "fk", "grey"), ("data_layer_id", "fk", "grey")])
d.add("protein_ligand_hits", 0, 2, "red", [
    ("id", "pk"), ("protein_id", "fk", "indigo"), ("ligand_id", "fk", "purple"),
    ("hit_score",), ("role",), ("hitset_id",)], accent=True)
d.add("ligands", 1, 2, "purple", [
    ("id", "pk"), ("smiles",), ("inchikey",), ("source",), ("source_molecule_id",)])
d.add("docking_results", 3, 2, "slate", [
    ("id", "pk"), ("job_id", "fk", "red"), ("ligand_id", "fk", "purple"),
    ("pocket_id", "fk", "amber"), ("dock_score",), ("n_poses",), ("pose_ref",), ("status",),
    ("cache_key", "fk", "grey"), ("data_layer_id", "fk", "grey")])
d.add("ground_truth_poses", 4, 2, "slate", [
    ("id", "pk"), ("protein_id", "fk", "indigo"), ("ligand_id", "fk", "purple"),
    ("structure_id", "fk", "teal"), ("pocket_id", "fk", "amber"), ("source",),
    ("source_system_id",), ("pose_ref",)])

px, py, pw, ph = d.geom("proteins")
sx, sy, sw, sh = d.geom("structures")
jx, jy, jw, jh = d.geom("protein_docking_jobs")
rx, ry, rw, rh = d.geom("protein_reference_frames")
ax, ay, aw, ah = d.geom("structure_chain_anchors")
kx, ky, kw, kh = d.geom("pockets")
gx, gy, gw, gh = d.geom("ground_truth_poses")
lx, ly, lw, lh = d.geom("ligands")

d.straight("mutations", "transformation_id", "transformations")
d.straight("transformations", "source_protein_id", "proteins")
d.straight("transformations", "target_protein_id", "proteins")
d.straight("structure_protein_relatability", "protein_id", "proteins", side="L")
d.straight("structure_protein_relatability", "structure_id", "structures")
d.straight("protein_ligand_hits", "ligand_id", "ligands")
d.straight("docking_results", "ligand_id", "ligands", side="L")

d.edge([(ax + 150, ay - 13), (ax + 150, 400), (sx + 70, 400), (sx + 70, sy + sh + 13)])
d.link("structure_chain_anchors", "reference_protein_id", (1150, py + ph + 13), side="L",
       mids=[(1272, d.row_y("structure_chain_anchors", "reference_protein_id")), (1272, 392), (1150, 392)])
d.edge([(kx + 210, ky - 13), (kx + 210, sy + sh + 13)])
d.edge([(kx + 305, ky - 13), (kx + 305, 78), (1150, 78), (1150, py - 13)])
d.edge([(jx + 105, jy - 13), (jx + 105, py + ph + 13)])
d.edge([(jx + 265, jy - 13), (jx + 265, py + ph + 13)])
d.edge([(rx + 110, ry - 13), (rx + 110, 336), (900, 336), (900, py + ph + 13)])
d.edge([(rx + 250, ry - 13), (rx + 250, 362), (952, 362), (952, py + ph + 13)])
d.link("protein_ligand_hits", "protein_id", (1060, py - 13), side="L",
       mids=[(22, d.row_y("protein_ligand_hits", "protein_id")), (22, 46), (1060, 46)])
d.link("docking_results", "job_id", (jx + jw / 2 + 60, jy + jh + 13), side="L",
       mids=[(COL[3] - 60, d.row_y("docking_results", "job_id")), (COL[3] - 60, jy + jh + 55),
             (jx + jw / 2 + 60, jy + jh + 55)])
d.link("docking_results", "pocket_id", (kx + 95, ky + kh + 13),
       mids=[(COL[4] - 30, d.row_y("docking_results", "pocket_id")), (COL[4] - 30, ky + kh + 50),
             (kx + 95, ky + kh + 50)])
d.edge([(gx + 310, gy - 13), (gx + 310, ky + kh + 13)])
d.link("ground_truth_poses", "structure_id", (sx + sw + 13, sy + sh - 40),
       mids=[(2115, d.row_y("ground_truth_poses", "structure_id")), (2115, sy + sh - 40)])
d.link("ground_truth_poses", "ligand_id", (lx + lw / 2 + 55, ly + lh + 13), side="L",
       mids=[(COL[4] - 18, d.row_y("ground_truth_poses", "ligand_id")), (COL[4] - 18, 1205),
             (lx + lw / 2 + 55, 1205)])

d.write(sys.argv[1] if len(sys.argv) > 1 else "erd.svg")
