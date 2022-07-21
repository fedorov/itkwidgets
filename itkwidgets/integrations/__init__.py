import itkwasm
import numpy as np
import zarr

from .dask import HAVE_DASK, dask_array_to_ndarray
from .itk import HAVE_ITK, itk_image_to_wasm_image, itk_group_spatial_object_to_wasm_point_set
from .pytorch import HAVE_TORCH
from .vtk import HAVE_VTK, vtk_image_to_ndarray, vtk_polydata_to_vtkjs
from .xarray import HAVE_XARRAY, xarray_data_array_to_numpy, xarray_data_set_to_numpy
from ..render_types import RenderType

_image_count = 1

async def _set_viewer_image(itk_viewer, image, ui, name=None):
    global _image_count
    if isinstance(image, itkwasm.Image):
        if not name:
            name = image.name
            if not name:
                name = f"image {_image_count}"
                _image_count += 1
        await itk_viewer.setImage(image, ui, name)
    elif isinstance(image, np.ndarray):
        if not name:
            name = f"image {_image_count}"
            _image_count += 1
        await itk_viewer.setImage(image, ui, name)
    elif isinstance(image, zarr.Group):
        if not name:
            name = f"image {_image_count}"
            _image_count += 1
        await itk_viewer.setImage(image, ui, name)
    elif HAVE_ITK:
        import itk
        if isinstance(image, itk.Image):
            wasm_image = itk_image_to_wasm_image(image)
            name = image.GetObjectName()
            if not name:
                name = f"image {_image_count}"
                _image_count += 1
            await itk_viewer.setImage(wasm_image, ui, name)
    if HAVE_VTK:
        import vtk
        if isinstance(image, vtk.vtkImageData):
            ndarray = vtk_image_to_ndarray(image)
            if not name:
                name = f"image {_image_count}"
                _image_count += 1
            await itk_viewer.setImage(ndarray, ui, name)
    if HAVE_DASK:
        import dask
        if isinstance(image, dask.array.core.Array):
            ndarray = dask_array_to_ndarray(image)
            name = image.name
            if not name:
                name = f"image {_image_count}"
                _image_count += 1
            await itk_viewer.setImage(ndarray, ui, name)
    if HAVE_TORCH:
        import torch
        if isinstance(image, torch.Tensor):
            if not name:
                name = f"image {_image_count}"
                _image_count += 1
            await itk_viewer.setImage(image.numpy(), ui, name)
    if HAVE_XARRAY:
        import xarray
        if isinstance(image, xarray.DataArray):
            ndarray = xarray_data_array_to_numpy(image)
            name = image.name
            if not name:
                name = f"image {_image_count}"
                _image_count += 1
            await itk_viewer.setImage(ndarray, ui, name)
        if isinstance(image, xarray.Dataset):
            ndarray = xarray_data_set_to_numpy(image)
            if not name:
                name = f"image {_image_count}"
                _image_count += 1
            await itk_viewer.setImage(ndarray, ui, name)


async def _set_viewer_point_sets(itk_viewer, point_sets, ui):
    if isinstance(point_sets, itkwasm.PointSet):
        await itk_viewer.setPointSets(point_sets, ui)
    elif isinstance(point_sets, np.ndarray):
        await itk_viewer.setPointSets(point_sets, ui)
    elif isinstance(point_sets, zarr.Group):
        await itk_viewer.setPointSets(point_sets, ui)
    elif HAVE_ITK:
        import itk
        if isinstance(point_sets, itk.GroupSpatialObject):
            wasm_point_sets = itk_group_spatial_object_to_wasm_point_set(point_sets)
            await itk_viewer.setPointSets(wasm_point_sets,ui)
    if HAVE_VTK:
        import vtk
        if isinstance(point_sets, vtk.vtkPolyData):
            vtkjs_polydata = vtk_polydata_to_vtkjs(point_sets)
            await itk_viewer.setPointSets(vtkjs_polydata,ui)
    if HAVE_DASK:
        import dask
        if isinstance(point_sets, dask.array.core.Array):
            ndarray = dask_array_to_ndarray(point_sets)
            await itk_viewer.setPointSets(ndarray,ui)
    if HAVE_TORCH:
        import torch
        if isinstance(point_sets, torch.Tensor):
            await itk_viewer.setPointSets(point_sets.numpy(), ui)
    if HAVE_XARRAY:
        import xarray
        if isinstance(point_sets, xarray.DataArray):
            ndarray = xarray_data_array_to_numpy(point_sets)
            await itk_viewer.setPointSets(ndarray, ui)
        if isinstance(point_sets, xarray.Dataset):
            ndarray = xarray_data_set_to_numpy(point_sets)
            await itk_viewer.setPointSets(ndarray, ui)


def _detect_render_type(data, input_type) -> RenderType:
    if isinstance(data, itkwasm.Image):
        return RenderType.IMAGE
    elif isinstance(data, itkwasm.PointSet):
        return RenderType.POINT_SET
    elif isinstance(data, np.ndarray):
        if input_type == 'point_sets':
            return RenderType.POINT_SET
        else:
            return RenderType.IMAGE
    elif isinstance(data, zarr.Group):
        if input_type == 'point_sets':
            return RenderType.POINT_SET
        else:
            return RenderType.IMAGE
    elif HAVE_ITK:
        import itk
        if isinstance(data, itk.Image):
            return RenderType.IMAGE
        elif isinstance(data, itk.GroupSpatialObject):
            return RenderType.POINT_SET
    if HAVE_VTK:
        import vtk
        if isinstance(data, vtk.vtkImageData):
            return RenderType.IMAGE
        elif isinstance(data, vtk.vtkPolyData):
            return RenderType.POINT_SET
    if HAVE_DASK:
        import dask
        if isinstance(data, dask.array.core.Array):
            if input_type == 'point_sets':
                return RenderType.POINT_SET
            else:
                return RenderType.IMAGE
    if HAVE_TORCH:
        import torch
        if isinstance(data, torch.Tensor):
            if input_type == 'point_sets':
                return RenderType.POINT_SET
            else:
                return RenderType.IMAGE
    if HAVE_XARRAY:
        import xarray
        if isinstance(data, xarray.DataArray):
            if input_type == 'point_sets':
                return RenderType.POINT_SET
            else:
                return RenderType.IMAGE
        if isinstance(data, xarray.Dataset):
            if input_type == 'point_sets':
                return RenderType.POINT_SET
            else:
                return RenderType.IMAGE
