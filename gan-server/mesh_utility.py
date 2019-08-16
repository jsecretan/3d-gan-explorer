## Utility functions to help decimate the mesh
from vtk import (vtkSphereSource, vtkPolyData, vtkDecimatePro)
import vtk
import numpy as np
import trimesh

def mkVtkIdList(it):
    vil = vtk.vtkIdList()
    for i in it:
        vil.InsertNextId(int(i))
    return vil

def getCellIds(cells):
    ids = []
    idList = vtk.vtkIdList()
    cells.InitTraversal()
    while cells.GetNextCell(idList):
        for i in range(0, idList.GetNumberOfIds()):
            pId = idList.GetId(i)
            ids.append(pId)
    ids = np.array(ids)
    return ids

def trimesh_to_vtk(mesh):

    vtkMesh = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    polys = vtk.vtkCellArray()

    for i, xi in enumerate(mesh.vertices):
        points.InsertPoint(i, xi)
    for pt in mesh.faces:
        polys.InsertNextCell(mkVtkIdList(pt))

    vtkMesh.SetPoints(points)
    vtkMesh.SetPolys(polys)

    return vtkMesh

def vtk_to_trimesh(vtkMesh):
    points = vtkMesh.GetPoints()
    polys = vtkMesh.GetPolys()

    vertices = []
    faces = []

    for i in range(points.GetNumberOfPoints()):
        vertices.extend(points.GetPoint(i))

    faces = getCellIds(polys).reshape((-1,3))

    return trimesh.base.Trimesh(vertices = np.array(vertices).reshape((-1,3)), faces = faces)

def decimate(mesh):

    vtkMesh = trimesh_to_vtk(mesh)

    decimate = vtkDecimatePro()
    decimate.SetInputData(vtkMesh)
    decimate.SetTargetReduction(.50)
    decimate.Update()

    decimatedPoly = vtkPolyData()
    decimatedPoly.ShallowCopy(decimate.GetOutput())

    return vtk_to_trimesh(decimatedPoly)